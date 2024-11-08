from django.core.mail import send_mail
import random
import string
import time
import redis

from django.conf import settings
from drf_yasg.openapi import Response

redis_conn = redis.StrictRedis(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)

# OTP saqlash uchun oddiy lug'at
otp_storage = {}

def generate_otp(phone_number_or_email: str,
                 expire_in: int = 120,
                 check_if_exists: bool=True) -> tuple[str, str]:
    if check_if_exists and phone_number_or_email in otp_storage:
        # Agar OTP mavjud bo'lsa va muddat o'tmagan bo'lsa, qaytarish
        stored_otp, timestamp = otp_storage[phone_number_or_email]
        if time.time() - timestamp < expire_in:
            return stored_otp, "OTP already exists and is valid."
    # Yangi OTP yaratish
    otp_code = ''.join(random.choices(string.digits, k=6))  # 6 raqamli OTP
    otp_secret = ''.join(random.choices(string.ascii_letters + string.digits, k=16))  # 16 belgidan iborat sir
    # Yangilangan OTP va vaqtni saqlash
    otp_storage[phone_number_or_email] = (otp_code, time.time())
    return otp_code, otp_secret

def send_email(email, otp_code):
    subject = "Your OTP code"
    message = f"Your OTP code is: {otp_code}"
    from_email = "tolibjonovabdulhay200@gmail.com" # Replace with your actual email
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)