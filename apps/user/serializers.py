from signal import pthread_sigmask

from rest_framework import serializers
from .models import User
from share.utils import check_otp


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number", "email", "password"]
        extra_kwargs = {
            "password": {"write_only": True}, # Password should not be returned in response
        }

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

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'gender', 'first_name', 'last_name', 'phone_number',
            'email', 'user_trade_role', 'company', 'photo',
            'bio', 'birth_date', 'country', 'city',
            'district', 'street_address', 'postal_code',
            'second_phone_number', 'building_number', 'apartment_number'
        ]