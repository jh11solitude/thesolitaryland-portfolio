from pathlib import Path
from decouple import config

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────

# Build paths like this: BASE_DIR / 'subdir'
# BASE_DIR points to the root of the project (where manage.py lives)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# __file__ = config/settings/base.py
# .parent   = config/settings/
# .parent   = config/
# .parent   = project root  ← this is BASE_DIR


# ─────────────────────────────────────────────
# SECURITY
# ─────────────────────────────────────────────

SECRET_KEY = config('SECRET_KEY')
# config() reads from .env — never hardcode secrets


# ─────────────────────────────────────────────
# APPLICATIONS
# ─────────────────────────────────────────────

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    # We'll add DRF and others here later
]

LOCAL_APPS = [
    'apps.portfolio',
    'apps.pages',
    'apps.contact',
]

# Django reads INSTALLED_APPS in order — structure matters
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# ─────────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────────

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ─────────────────────────────────────────────
# URLS & WSGI
# ─────────────────────────────────────────────

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'


# ─────────────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────────────

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Global templates folder
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


# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='thesolitaryland_portfolio'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}


# ─────────────────────────────────────────────
# STATIC & MEDIA FILES
# ─────────────────────────────────────────────

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']   # Where YOUR static files live
STATIC_ROOT = BASE_DIR / 'staticfiles'     # Where collectstatic puts them for production

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Uploaded files (photos, videos, thumbnails) go into /media/
# In production this moves to S3 or similar cloud storage


# ─────────────────────────────────────────────
# INTERNATIONALISATION
# ─────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Singapore'
USE_I18N = True
USE_TZ = True


# ─────────────────────────────────────────────
# DEFAULT PRIMARY KEY TYPE
# ─────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# BigAutoField = 64-bit integer IDs
# Future-proofs against running out of IDs in large tables