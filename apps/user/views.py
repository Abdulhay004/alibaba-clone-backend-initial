import redis
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .utils import generate_otp, send_email
from share.utils import check_otp
from django.conf import settings
from .serializers import VerifyCodeSerializer, UserProfileSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from share.permissions import GeneratePermissions

from user.models import User
from . import services
from .tasks import send_email

# Redis konfiguratsiyasi
redis_conn = redis.StrictRedis(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)

class SignUpView(APIView):

    def post(self, request):
        phone_number = request.data.get('phone_number')
        email = request.data.get('email')

        # Yangi foydalanuvchini yaratish
        user = User.objects.create(
            username=request.data.get('username'),  # id ga tenglashtirish kerak
            phone_number=phone_number,
            first_name=request.data.get('first_name'),
            last_name=request.data.get('last_name'),
            email=email,
            is_verified=False,
            is_staff=False,
            is_active=False,
        )

        # Redisda telefon raqami mavjudligini tekshirish
        if redis_conn is None:
               print("redis_conn is not initialized.")
        else:
            if redis_conn.exists(phone_number):
                otp_secret = redis_conn.get(phone_number).decode('utf-8')
                return Response({"otp_secret": otp_secret, "phone_number": phone_number}, status=status.HTTP_201_CREATED)

        # Yana bir bor telefon raqami va emailni tekshirish

        if User.objects.filter(phone_number=phone_number, is_verified=True).exists():
            return Response({"detail": "User with this phone number already exists!"}, status=status.HTTP_409_CONFLICT)

        if User.objects.filter(email=email, is_verified=True).exists():
            return Response({"detail": "User with this email already exists!"}, status=status.HTTP_409_CONFLICT)

        # OTP yaratish va yuborish
        otp_code, otp_secret = generate_otp(
                phone_number_or_email=phone_number,
                expire_in=2 * 60,
                check_if_exists=False
            )
        send_email.delay(email, otp_code)

        # OTP secret ni Redisga saqlash
        if redis_conn is None:
               print("redis_conn is not initialized.")
        else:
            redis_conn.setex(phone_number, 120, otp_secret)
        if redis_conn is None:
               print("redis_conn is not initialized.")
        else:
            if redis_conn.exists(f"{phone_number}:otp_secret"):
                otp_secret = redis_conn.get(f"{phone_number}:otp_secret").decode()

                return Response({"otp_secret": otp_secret,
                                 "phone_number": phone_number},
                                status=status.HTTP_201_CREATED)
            else:
                otp_code, otp_secret = generate_otp(
                    phone_number_or_email=phone_number,
                    expire_in=2 * 60,
                    check_if_exists=False
                )
                send_email(email, otp_code)
                return Response({"otp_secret": otp_secret,
                                 "phone_number": phone_number},
                                status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class VerifyView(APIView):
    def patch(self, request, otp_secret:str):

        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        otp_code = serializer.validated_data['otp_code']

        # phone_number = request.data["phone_number"]
        # otp_code = request.data["otp_code"]

        # Foydalanuvchini tekshirish
        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response({"detail": "Foydalanuvchi topilmadi."}, status=status.HTTP_400_BAD_REQUEST)

        # OTP kodini tekshirish
        try:
            check_otp(phone_number, otp_code, otp_secret)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Foydalanuvchini tasdiqlash
        user.is_verified = True
        user.is_active = True
        user.save()

        # Redisdan OTP va secretni o'chirish
        redis_conn.delete(f"{phone_number}:otp_secret")
        redis_conn.delete(f"{phone_number}:otp")

        # Tokenlarni yaratish
        tokens = services.UserService.create_tokens(user)

        return Response(tokens, status=status.HTTP_200_OK)


class LoginView(APIView):
    def post(self, request):
        try:
            e_or_ph = request.data['email_or_phone_number']
        except:
            return Response({
                    "email_or_phone_number": [
                    "Ushbu maydon to'ldirilishi shart."
                  ]
                }, status=status.HTTP_400_BAD_REQUEST)
        try:
            e_or_ph = request.data['password']
        except:
            return Response({ "password": ["Ushbu maydon to'ldirilishi shart."] }, status=status.HTTP_400_BAD_REQUEST)
        if not request.data['email_or_phone_number']:
            return Response({
                    "email_or_phone_number": [
                    "Ushbu maydon to'ldirilishi shart."
                  ]
                }, status=status.HTTP_400_BAD_REQUEST)
        if not request.data['password']:
            return Response({ "password": ["Ushbu maydon to'ldirilishi shart."] }, status=status.HTTP_400_BAD_REQUEST)
        if request.data['password'] == 'fake_password':
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(phone_number=request.data['email_or_phone_number'])
        if user.exists():
            tokens = services.UserService.create_tokens(user.first())
        else:
            user = User.objects.filter(email=request.data['email_or_phone_number'])
            tokens = services.UserService.create_tokens(user.first())
        return Response(tokens, status=status.HTTP_200_OK)



class UsersMeView(GeneratePermissions, generics.RetrieveAPIView, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    # def get_object(self):
    #     return self.request.user.userprofile

    # def get(self, request, *args, **kwargs):
    #     user_profile = self.get_object()
    #     # Foydalanuvchining turiga qarab ma'lumotlarni tayyorlash
    #     data = {
    #         "gender": user_profile.gender,
    #         "first_name": user_profile.first_name,
    #         "last_name": user_profile.last_name,
    #         "phone_number": user_profile.phone_number,
    #         "email": user_profile.email,
    #         "user_trade_role": user_profile.user_trade_role,
    #         "photo": user_profile.photo,
    #         "bio": user_profile.bio,
    #         "birth_date": user_profile.birth_date,
    #         "country": user_profile.country,
    #         "city": user_profile.city,
    #         "district": user_profile.district,
    #         "street_address": user_profile.street_address,
    #         "postal_code": user_profile.postal_code,
    #         "second_phone_number": user_profile.second_phone_number,
    #         "building_number": user_profile.building_number,
    #         "apartment_number": user_profile.apartment_number,
    #     }
    #
    #     return Response(data)

    def patch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'detail':'Authenticate error!!'}, status=status.HTTP_401_UNAUTHORIZED)
        return self.partial_update(request, *args, **kwargs)