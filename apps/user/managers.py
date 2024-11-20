from django.contrib.auth.models import BaseUserManager
from decouple import config

class CustomUserManager(BaseUserManager):
    def create_user(self,email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email kiritish shart.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser uchun is_staff = True bo\'lishi shart.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser uchun is_superuser = True bo\'lishi shart.')

        return self.create_user(email=config('DJANGO_SUPERUSER_EMAIL'), password=config('DJANGO_SUPERUSER_PASSWORD'), **extra_fields)