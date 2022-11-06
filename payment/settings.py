"""
Django settings for payment project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os
import decimal
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA256
import environ
from datetime import timedelta
from rest_framework.settings import api_settings


AUTH_USER_MODEL = 'account.Account'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Initialize environment variables
env = environ.Env()
environ.Env.read_env()

# MY CONSTANTS:
ELECTRUM                = env('ELECTRUM_PATH')
WALLET_DIR              = env('WALLET_DIR')
TIME_CHECK              = 7 # minutes
DELETE_PRICE_DAYS       = 5 # delete CryptoPrice objects older than this many days.
PAY_REQUEST_EXPIRY      = 259200 # seconds. 3 days
JSON_RPC                = f"http://{env('RPC_USER')}:{env('RPC_PASS')}@127.0.0.1:{env('RPC_PORT')}"
WALLET_PASS             = env('WALLET_PASS')
COINS_LONG              = env('COINS_LONG')
COINS_SHORT             = env('COINS_SHORT')
COINMARKETCAP_API_KEY   = env('COINMARKETCAP_API_KEY')
CAD_MIN_ALLOWANCE       = decimal.Decimal(0.95)
BTC_MIN_ALLOWANCE       = decimal.Decimal(0.98)
OVERPAYMENT_THRESH      = decimal.Decimal(1.2)

# django-cryptography module settings:
CRYPTOGRAPHY_BACKEND = default_backend()
CRYPTOGRAPHY_DIGEST = SHA256
CRYPTOGRAPHY_KEY = None     #None means Django will automatically generate one for me
CRYPTOGRAPHY_SALT = 'django-cryptography'
# SIGNING_BACKEND = 'django_cryptography.core.signing.TimestampSigner'

# CELERY CONSTANtS
CELERY_BROKER_URL = 'amqp://localhost'


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'knox.auth.TokenAuthentication',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    }
}

REST_KNOX = {
  'SECURE_HASH_ALGORITHM': 'cryptography.hazmat.primitives.hashes.SHA512',
  'AUTH_TOKEN_CHARACTER_LENGTH': 64,
  'TOKEN_TTL': timedelta(hours=10),
  'USER_SERIALIZER': 'knox.serializers.UserSerializer',
  'TOKEN_LIMIT_PER_USER': None,
  'AUTO_REFRESH': False,
  'EXPIRY_DATETIME_FORMAT': api_settings.DATETIME_FORMAT,
}




# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.1.65',
    'testserver',
    ]

#APPEND_SLASH = False

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'knox',
    'django_extensions',
    # 'rest_framework_hmac.hmac_key',
    'psycopg2',
    'django_celery_beat',
    'payment.account',
    'payment.error',
    'payment.hmac_auth',
    'payment.plan',
    'payment.price',
    'payment.wallet',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'payment.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'payment.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE'  : 'django.db.backends.sqlite3',
    #     'NAME'    : BASE_DIR / 'db.sqlite3',
    # }
    'default': {
        'ENGINE'    : 'django.db.backends.postgresql_psycopg2',
        'NAME'      : env('DB_NAME'),
        'USER'      : env('DB_USER'),
        'PASSWORD'  : env('DB_PASSWORD'),
        'HOST'      : env('DB_HOST'),
        'PORT'      : '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR /'static'

STATICFILES_DIRS = [
    'payment/static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media/')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Enables Django Messages. Boilerplate from Django docs!
from django.contrib.messages import constants as messages
MESSAGE_TAGS= {
    messages.ERROR: 'danger',
}
