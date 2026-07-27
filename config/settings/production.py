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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


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
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER', default='noreply@thesolitaryland.com')
CONTACT_EMAIL = config('CONTACT_EMAIL', default='thesolitaryland11@gmail.com')

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