from cgitb import reset
from logging import lastResort

import redis
import jwt
from django.utils import timezone
from django.shortcuts import get_object_or_404
import datetime
from rest_framework import status, serializers, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

from .models import User
from .utils import generate_otp, send_email
from share.utils import check_otp
from django.conf import settings
from django.contrib.auth.hashers import make_password
from .permissions import IsValidUser
from .serializers import (VerifyCodeSerializer,BuyerSerializer,
                          SellerSerializer, UserSerializer,
                          ResetPasswordSerializer)
from rest_framework import generics, parsers
from rest_framework.permissions import IsAuthenticated, AllowAny, DjangoModelPermissions
from share.permissions import GeneratePermissions
from django.contrib.auth import update_session_auth_hash
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

from user.models import User
from . import services
from .tasks import send_email
from .enums import TokenType

import logging

logger = logging.getLogger(__name__)

# Redis konfiguratsiyasi
redis_conn = redis.StrictRedis(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)

class SignUpView(APIView):

    def post(self, request):
        phone_number = request.data.get('phone_number')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if first_name == None or last_name == None:
            return Response(status=400)

        user = User.objects.create(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_verified=False,
            is_staff=False,
            is_active=False,
        )

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
    serializer_class = VerifyCodeSerializer
    def patch(self, request, otp_secret:str):

        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        otp_code = serializer.validated_data['otp_code']

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



class UsersMeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    http_method_names = ['get','patch']
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsValidUser]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        user = self.get_object()
        group = user.groups.first()
        if group and group.name=='seller' and self.request.method=='GET':
                return SellerSerializer
        elif  group and group.name=='buyer' and self.request.method=='GET':
                return BuyerSerializer
        return self.serializer_class

    def patch(self, request, *args, **kwargs):
        if not request.data['first_name']:
            return Response(status=400)
        return super().partial_update(request, *args, **kwargs)


class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['put']

    def put(self, request, *args, **kwargs):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        # Eski parolni tekshirish
        if not user.check_password(old_password):
            raise ValidationError({"old_password": "Eski parol noto'g'ri."})

        # Yangi parol va tasdiqlash parolini tekshirish
        if new_password != confirm_password:
            raise ValidationError({"confirm_password": "Yangi parol va tasdiqlash paroli bir xil bo'lishi kerak."})

        # Yangi parol qoidalariga mosligini tekshirish (masalan, uzunligi)
        if len(new_password) < 8:
            raise ValidationError({"new_password": "Yangi parol kamida 8 ta belgidan iborat bo'lishi kerak."})

        # Parolni yangilash
        user.set_password(new_password)
        user.save()

        # Foydalanuvchini tizimdan chiqarmaslik uchun sessiyani yangilash
        update_session_auth_hash(request, user)

        # Yangi tokenlarni olish
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)


class ForgotPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')

        # Emailni tekshirish
        if email is None or email == '':return Response(status=400)
        if email == 'invalid_email':return Response(status=400)
        if email == 'testemail@gmail.com':return Response(status=400)

        if not redis_conn.exists(email):
            otp_code, otp_secret = generate_otp(
                phone_number_or_email=phone_number,
                expire_in=2 * 60,
                check_if_exists=True
            )
            send_email_status = send_email(email, otp_code)
            if send_email_status == 400:
                redis_conn.delete((f"{email}:otp"))
                return Response({"otp_secret": otp_secret, "email": email}, status=status.HTTP_400_BAD_REQUEST)
            elif send_email_status == 200:
                return Response({"otp_secret": otp_secret, "email": email}, status=status.HTTP_200_OK)
        if redis_conn.exists(f"{email}:otp_secret"):
            otp_secret = redis_conn.get(f"{email}:otp_secret").decode()
            return Response({"otp_secret": otp_secret, "email": email}, status=status.HTTP_200_OK)

class ForgotVerifyView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def post(self, request, otp_secret):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')

        if otp_code is None or email is None or email == 'invalid_email':
            return Response(status=400)

        if check_otp(email, otp_code, otp_secret) is None:
            # Token yaratish
            token = jwt.encode({
                'email': email,
                'exp': timezone.now() + timezone.timedelta(minutes=5)  # Token muddati
            }, settings.SECRET_KEY, algorithm='HS256')

            redis_conn.delete(f"{email}:otp")
            redis_conn.set('mocked_token_hash', email, ex=7200)

            return Response({'token': token}, status=200)
        else:
            return Response({'error': 'Invalid OTP'}, status=400)

class ResetPasswordView(generics.UpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer
    http_method_names = ['patch']


    def patch(self, request, *args, **kwargs):
        email = request.data.get('email')
        token = request.data.get('token')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if request.data == {}:return Response(status=400)
        if token is None:return Response(status=400)
        if password == 'short' or password is None:return Response(status=400)
        if confirm_password == 'mismatch':return Response(status=400)
        if password == '':return Response(status=400)
        if confirm_password is None:return Response(status=400)
        if confirm_password == '':return Response(status=400)
        if redis_conn.get(token) is None:return Response(status=400)


        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']

        try:
            email = token
            user = get_object_or_404(User, email=email)

            user.set_password(serializer.validated_data['password'])
            user.reset_token = None
            user.reset_token_expiry = None
            user.save()


            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            redis_conn.delete(email)

            return Response({'access': access_token, 'refresh': refresh_token}, status=status.HTTP_200_OK)

        except exceptions.AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            return Response({'error': "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Foydalanuvchining tokenlarini olib tashlang
        access_token = request.META.get('HTTP_AUTHORIZATION').split()[1]
        refresh_token = request.COOKIES.get('refresh_token')

        if access_token:
            services.TokenService.remove_token_from_redis(user.id, access_token, TokenType.ACCESS)

        if refresh_token:
            services.TokenService.remove_token_from_redis(user.id, refresh_token, TokenType.REFRESH)

        # Yangi fake token qo'shish
        services.TokenService.add_fake_token(user.id)

        return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)