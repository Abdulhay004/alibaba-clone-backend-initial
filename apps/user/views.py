import redis
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .utils import generate_otp, send_email
from share.utils import check_otp
from django.conf import settings
from .serializers import VerifyCodeSerializer
from user.models import User
from . import services

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
        send_email(email, otp_code)

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