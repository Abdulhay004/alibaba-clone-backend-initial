import redis
import datetime
from django.conf import settings

from .enums import TokenType


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