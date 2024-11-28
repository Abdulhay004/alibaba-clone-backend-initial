import redis
import jwt
import datetime
from django.conf import settings
from typing import Union
from uuid import UUID
from rest_framework.exceptions import ValidationError
from .models import User
from .enums import TokenType

redis_conn = redis.StrictRedis(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)


ALGORITHM = "HS256"

class UserService:
    @classmethod
    def authenticate(cls, email_or_phone_number: str, password: str, quiet=False) -> Union[ValidationError, User, None]:
        # Foydalanuvchini tekshirish jarayoni
        user = cls.get_user_by_email_or_phone(email_or_phone_number)

        if not user or not user.is_verified:
            if not quiet:
                raise ValueError("Tasdiqlanmagan foydalanuvchi topilmadi!")
            return None

        if user.password != password:
            return None  # Parol noto'g'ri

        return user

    @classmethod
    def create_tokens(cls, user: User, access: str = None, refresh: str = None) -> dict[str, str]:
        # Tokenlarni yaratish jarayoni
        access_token = access or cls.generate_access_token(user)
        refresh_token = refresh or cls.generate_refresh_token(user)

        return {
            "access": access_token,
            "refresh": refresh_token
        }

    @classmethod
    def get_user_by_email_or_phone(cls, email_or_phone_number: str) -> User:
        if User.objects.filter(phone_number=email_or_phone_number).exists():
            return User.objects.filter(phone_number=email_or_phone_number).first()
        if User.objects.filter(email=email_or_phone_number).exists():
            return User.objects.filter(email=email_or_phone_number).first()


    @classmethod
    def generate_access_token(cls, user: User) -> str:
        payload = {
            "sub": str(user.id),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
        return token

    @classmethod
    def generate_refresh_token(cls, user: User) -> str:
        payload = {
            "sub": str(user.id),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
        return token

class TokenService:
    @classmethod
    def get_redis_client(cls) -> redis.Redis:
        return redis.Redis.from_url(settings.REDIS_URL)

    @classmethod
    def get_valid_tokens(cls, user_id: int, token_type: TokenType) -> set:
        redis_client = cls.get_redis_client()
        token_key = f"user:{user_id}:{token_type}"
        valid_tokens = redis_client.smembers(token_key)
        return valid_tokens

    @classmethod
    def add_token_to_redis(
            cls,
            user_id: int,
            token: str,
            token_type: TokenType,
            expire_time: datetime.timedelta,
    ) -> None:
        redis_client = cls.get_redis_client()

        token_key = f"user:{user_id}:{token_type}"

        valid_tokens = cls.get_valid_tokens(user_id, token_type)
        if valid_tokens:
            cls.delete_tokens(user_id, token_type)
        redis_client.sadd(token_key, token)
        redis_client.expire(token_key, expire_time)

    @classmethod
    def delete_tokens(cls, user_id: int, token_type: TokenType) -> None:
        redis_client = cls.get_redis_client()
        token_key = f"user:{user_id}:{token_type}"
        valid_tokens = redis_client.smembers(token_key)
        if valid_tokens is not None:
            redis_client.delete(token_key)
