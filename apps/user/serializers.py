from rest_framework import serializers
from .models import User, Group, BuyerUser, SellerUser
from share.enums import UserRole
from django.core.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    user_trade_role = serializers.ChoiceField(choices=[UserRole.BUYER.value,UserRole.SELLER.value],write_only=True)
    confirm_password = serializers.CharField(required=True,write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['gender','first_name','last_name','phone_number','email','password','confirm_password','user_trade_role']
        extra_kwargs = {'password':{'write_only':True}}

    def validate(self,data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password!=confirm_password:
            raise ValidationError({"detail":"Password and Confirm Password must be same"})
        return data

    def create(self, validated_data):
        user = User.objects.filter(phone_number=validated_data['phone_number'],email=validated_data['email']).first()
        if user:
            return user
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            gender = validated_data['gender'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number = validated_data['phone_number']
        )
        return user

class VerifyCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    otp_code = serializers.CharField(required=True)

    def validate(self, attrs):
        # Telefon raqami va OTP kodini tekshirish
        phone_number = attrs.get('phone_number')
        otp_code = attrs.get('otp_code')

        # Telefon raqami formatini tekshirish (agar kerak bo'lsa)
        if not self.is_valid_phone_number(phone_number):
            raise serializers.ValidationError("Noto'g'ri telefon raqami.")

        # OTP kodini tekshirish (agar kerak bo'lsa)
        if not self.is_valid_otp_code(otp_code):
            raise serializers.ValidationError("Noto'g'ri OTP kodi.")

        return attrs

# {'phone_number': '+998903785993', 'otp_code': '168467'}
    def is_valid_phone_number(self, phone_number):
        if phone_number[0] == '+' and len(phone_number[1:]) == 12:
            return True
        else:
            return False

    def is_valid_otp_code(self, otp_code):
        if len(otp_code) == 6:
            return True
        else:
            return False

class BuyerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    phone_number = serializers.CharField(max_length=50, required=False)
    gender = serializers.CharField(max_length=50, required=False)
    email = serializers.EmailField(required=False)
    class Meta:
        model = BuyerUser
        fields = [
            'id', 'gender', 'first_name', 'last_name',
            'phone_number','email', 'photo',
            'bio', 'birth_date', 'country', 'city', 'email',
            'district', 'street_address', 'postal_code',
            'second_phone_number', 'building_number', 'apartment_number'
        ]

class SellerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    phone_number = serializers.CharField(max_length=50, required=False)
    gender = serializers.CharField(max_length=50, required=False)
    email = serializers.EmailField(required=False)
    class Meta:
        model = SellerUser
        fields = [
            'id', 'gender', 'first_name', 'last_name',
            'phone_number','email', 'photo', 'company',
            'bio', 'birth_date', 'country', 'city', 'email',
            'district', 'street_address', 'postal_code',
            'second_phone_number', 'building_number', 'apartment_number'
        ]

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=8) # Enforce min length
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

