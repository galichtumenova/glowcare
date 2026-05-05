"""
Django settings for chkv_project project.
"""

from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


# ===== SECURITY =====

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-cm#5$u+arsermps2)5tjcar3n77sx50pe430h=0c#@)vivlx!%'
)

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']


# ===== APPS =====

INSTALLED_APPS = [
    'cloudinary',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts',
]


# ===== MIDDLEWARE =====

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ===== URLS / WSGI =====

ROOT_URLCONF = 'chkv_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'chkv_project.wsgi.application'


# ===== DATABASE =====

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}


# ===== PASSWORD VALIDATION =====

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


# ===== LANGUAGE / TIME =====

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Almaty'

USE_I18N = True
USE_TZ = True


# ===== STATIC FILES =====

STATIC_URL = '/static/'

STATICFILES_DIRS = []

if os.path.exists(BASE_DIR / 'static'):
    STATICFILES_DIRS.append(BASE_DIR / 'static')

STATIC_ROOT = BASE_DIR / 'staticfiles'


# ===== MEDIA / CLOUDINARY =====

MEDIA_URL = '/media/'

CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}


# ===== CUSTOM USER =====

AUTH_USER_MODEL = 'accounts.CustomUser'

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'


# ===== DEFAULT FIELD =====

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ===== TELEGRAM ORDER =====

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')


# ===== GEMINI AI =====

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')