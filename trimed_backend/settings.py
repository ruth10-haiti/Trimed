"""
Django settings for trimed_backend project.
"""

import os
from pathlib import Path
from datetime import timedelta
import dj_database_url
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-f4f5j7s&!r4j@y+qo(mc=l@039&%q&41+3rr_$dj51w5$&e_0j')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0,10.0.2.2,*.railway.app,*.onrender.com', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Applications tierces
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_yasg',
    'django_filters',
    'django_extensions',

    'gestion_tenants',
    'comptes',
    'patients',
    'medical',
    'gestion_medicaments',
    'rendez_vous',
    'facturation',
    'notifications',
    'hospitalisation',
    'salles_medicales',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'trimed_backend.middleware.TenantMiddleware',
    'trimed_backend.middleware.LoggingMiddleware',
    'trimed_backend.middleware.ExceptionHandlingMiddleware',
]

ROOT_URLCONF = 'trimed_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'trimed_backend.wsgi.application'

# Database configuration
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='postgresql://localhost:5432/Trimedh_BD'),
        conn_max_age=600
    )
}

# Modèle d'utilisateur personnalisé
AUTH_USER_MODEL = 'comptes.Utilisateur'

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = DEBUG

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# Configuration JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'USER_ID_FIELD': 'utilisateur_id',  
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}

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

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'America/Port-au-Prince'
USE_I18N = True
USE_TZ = True

if not DEBUG:
    CORS_ALLOWED_ORIGINS = config(
        'CORS_ALLOWED_ORIGINS',
        default='http://localhost:3000,http://127.0.0.1:3000,https://trimedh.vercel.app',
        cast=lambda v: [s.strip() for s in v.split(',')]
    )

CORS_ALLOW_CREDENTIALS = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_ROOT = '/opt/render/project/src/media/'

# Taille maximale des fichiers (10 MB)
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ✅ Brevo (Sendinblue) email configuration - CORRIGÉ
BREVO_API_KEY = config('BREVO_API_KEY', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@trimedhaiti.com')

# ✅ FRONTEND_URL corrigé pour la redirection
FRONTEND_URL = config('FRONTEND_URL', default='https://trimedh.vercel.app')

# ✅ BACKEND_URL pour les emails
BACKEND_URL = config('BACKEND_URL', default='https://trimedh-service.onrender.com')

# Email backend pour développement (console) - à changer en production
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'