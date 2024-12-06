from pathlib import Path
from datetime import timedelta
from decouple import config
import sys
import os
BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.append(os.path.join(BASE_DIR, 'apps'))
# kdkdkdsfjdfljsaflsdj


# SECRET_KEY = "django-inse-6+-l+d2fi3saztr*nqn#h214oi)!s98+bs%@0#d90ec4#g)69j"

# SUPERUSER_EMAIL = config('DJANGO_SUPERUSER_EMAIL')

# SECRET_KEY = "django-insecure-6+-l+d2fi3saztr*nqn#h214oi)!s98+bs%@0#d90ec4#g)69j"


SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG')

ALLOWED_HOSTS = []

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

EXTERNAL_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'django_redis',
    # 'django.contrib.contenttypes',
    # 'modeltranslation',
    # 'django_filters',
    # 'rest_framework.authtoken',
    'drf_yasg',
    # 'ckeditor',
    # 'ckeditor_uploader',
]


LOCAL_APPS = [
    'share',
    'user',
    'product',
    'cart',
]

INSTALLED_APPS = DJANGO_APPS + EXTERNAL_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
AUTH_USER_MODEL = 'user.User'

WSGI_APPLICATION = "core.wsgi.application"

AUTHENTICATION_BACKENDS = [
    'user.backends.CustomModelBackend',
]



# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
#         'NAME': config('DB_NAME', default='db.sqlite3'),
#         'USER': config('DB_USER', default=''),
#         'PASSWORD': config('DB_PASSWORD', default=''),
#         'HOST': config('DB_HOST', default=''),
#         'PORT': config('DB_PORT', default=''),
#     }
# }

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'user.authentications.CustomJWTAuthentication',
    ]
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_password'
DEFAULT_FROM_EMAIL = 'webmaster@example.com'

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# redis setup
REDIS_HOST = config('REDIS_HOST', default='localhost')
REDIS_PORT = config('REDIS_PORT', default='6379')
REDIS_DB = config('REDIS_DB', default='1')

REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}


# celery setup
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TIMEZONE = 'Asia/Tashkent'

# stripe setup

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),  # Tokenning amal qilish muddati
}


# logging setup

