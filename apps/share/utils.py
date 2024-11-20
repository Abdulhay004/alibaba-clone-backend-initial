# apps/share/utils.py
from typing import Union

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
import redis

from rest_framework.permissions import IsAuthenticated, AllowAny

from django.conf import settings


from user.models import Group
from user.models import User, Policy
redis_conn = redis.StrictRedis(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)

def add_permissions(obj: Union[User, Group, Policy], permissions: list[str]):
    def get_perm(perm: str)-> list:
        app_label, codename = perm.split('.')
        try:
            model = codename.split('_')[1]
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            permission, _ = Permission.objects.get_or_create(codename=codename, content_type=content_type,)
        except (IndexError, ContentType.DoesNotExist):
            permission, _ = Permission.objects.get_or_create(codename=codename)
        return permission
    if isinstance(obj, User):
        obj.user_permissions.clear()
        obj.user_permissions.add(*map(get_perm, permissions))
    elif isinstance(obj, Group) or isinstance(obj, Policy):
        obj.permissions.clear()
        obj.permissions.add(*map(get_perm, permissions))


def check_otp(phone_number_or_email: str, otp_code: str, otp_secret: str) -> None:
    stored_otp = redis_conn.get(f"otp:{phone_number_or_email}")
    stored_secret = redis_conn.get(f"otp_secret:{phone_number_or_email}")

    if stored_otp is None or stored_secret is None:
        raise ValueError("OTP yoki maxfiy kalit topilmadi.")
    if stored_otp.decode('utf-8') != otp_code or stored_secret.decode('utf-8') != otp_secret:
        raise ValueError("OTP kod yoki maxfiy kalit noto'g'ri.")

def check_perm(perm):
    """Checks permission based on a boolean value."""
    if perm:
        return [IsAuthenticated]
    else:
        return [AllowAny]