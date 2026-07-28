"""
Production settings for thesolitaryland-portfolio.
 
All secrets come from environment variables — never hardcoded.
This file is safe to commit to Git.
 
Environment variables required on Render:
  SECRET_KEY          — Django secret key (generate a new one for production)
  DATABASE_URL        — Provided automatically by Render PostgreSQL
  ALLOWED_HOSTS       — Your domain e.g. thesolitaryland.onrender.com,thesolitaryland.co
  CONTACT_EMAIL       — Where contact form submissions are emailed
  EMAIL_HOST          — SMTP host e.g. smtp.gmail.com
  EMAIL_PORT          — SMTP port e.g. 587
  EMAIL_HOST_USER     — SMTP login email
  EMAIL_HOST_PASSWORD — SMTP app password (not your main password)
"""


from .base import *
import dj_database_url
from decouple import config
import cloudinary

# ─────────────────────────────────────────────────────────────────
# CORE
# ─────────────────────────────────────────────────────────────────

DEBUG = False

SECRET_KEY = config('SECRET_KEY')

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    cast=lambda v: [s.strip() for s in v.split(',')]
)


# ─────────────────────────────────────────────────────────────────
# DATABASE
# Using dj-database-url to parse Render's DATABASE_URL string
# ─────────────────────────────────────────────────────────────────

DATABASES = {
    'default': dj_database_url.config(
        env='DATABASE_URL',
        conn_max_age=600,
        # conn_max_age=600 enables persistent connections
        # Reuses DB connections for up to 600s instead of
        # opening a new connection on every request
        ssl_require=True,
        # Render PostgreSQL requires SSL
    )
}

# ─────────────────────────────────────────────────────────────────
# STATIC FILES — WhiteNoise
# ─────────────────────────────────────────────────────────────────

# Insert WhiteNoise right after SecurityMiddleware
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# CompressedManifestStaticFilesStorage does two things:
# 1. Compresses static files (gzip + brotli) for faster delivery
# 2. Appends a content hash to filenames e.g. main.abc123.css
#    This enables infinite browser caching (file changes = new hash)
#
# NOTE: DEFAULT_FILE_STORAGE / STATICFILES_STORAGE were removed in Django 5.1.
# On Django 6.0 they are silently ignored, so both storage backends are
# configured together below via STORAGES (the "default" key is added once
# Cloudinary is configured further down this file).
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ─────────────────────────────────────────────────────────────────
# SECURITY HEADERS
# These tell browsers how to handle your site
# ─────────────────────────────────────────────────────────────────

# Force HTTPS for 1 year; include subdomains
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Redirect all HTTP requests to HTTPS
SECURE_SSL_REDIRECT = True

# Session cookie only sent over HTTPS
SESSION_COOKIE_SECURE = True

# CSRF cookie only sent over HTTPS
CSRF_COOKIE_SECURE = True

# Prevent browsers from guessing content types
SECURE_CONTENT_TYPE_NOSNIFF = True

# Enable browser XSS filtering
SECURE_BROWSER_XSS_FILTER = True

# Prevent clickjacking — your site can't be embedded in iframes
X_FRAME_OPTIONS = 'DENY'

# Render terminates SSL at the load balancer and forwards as HTTP
# This header tells Django the original request was HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# ─────────────────────────────────────────────────────────────────
# EMAIL
# ─────────────────────────────────────────────────────────────────

# Email — configure SMTP for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True

# The actual email address sending the alerts (e.g., your Gmail account)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')

# Your Google App Password (NOT your regular login password!)
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# The "From:" header clients see when they get an automated copy
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER')

# The "To:" destination where client portfolio inquiries actually land
CONTACT_EMAIL = config('CONTACT_EMAIL')

# ─────────────────────────────────────────────────────────────────
# CORS — restrict to your actual frontend domain in production
# ─────────────────────────────────────────────────────────────────

# Only allow your specific frontend domain in production
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://thesolitaryland-portfolio.onrender.com, https://thesolitaryland.co, https://www.thesolitaryland.co',
    cast=lambda v: [s.strip() for s in v.split(',')]
)


# ─────────────────────────────────────────────────────────────────
# CSRF — required since Django 4.0 for any cross-origin POST
# (e.g. the contact form) to a domain sitting behind Render's proxy
# ─────────────────────────────────────────────────────────────────

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://thesolitaryland-portfolio.onrender.com,https://thesolitaryland.co,https://www.thesolitaryland.co',
    cast=lambda v: [s.strip() for s in v.split(',')]
)


# ─────────────────────────────────────────────────────────────────
# LOGGING
# In production, log errors to stdout so Render captures them
# ─────────────────────────────────────────────────────────────────

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
        # Only WARNING and above goes to logs in production
        # This prevents flooding logs with DEBUG/INFO messages
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

INSTALLED_APPS += ['cloudinary', 'cloudinary_storage']

cloudinary.config(
    cloud_name=config('CLOUDINARY_CLOUD_NAME'),
    api_key=config('CLOUDINARY_API_KEY'),
    api_secret=config('CLOUDINARY_API_SECRET'),
    secure=True
)

# Override default file storage to use Cloudinary.
# This merges into the STORAGES dict set earlier in this file (which already
# holds the "staticfiles" key) rather than replacing it, so both the
# WhiteNoise static files backend and the Cloudinary media backend are active.
STORAGES["default"] = {
    "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
}