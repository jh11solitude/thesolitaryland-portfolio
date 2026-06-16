from .base import *
from decouple import config

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Django Debug Toolbar — shows SQL queries, cache hits, template context
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

INTERNAL_IPS = ['127.0.0.1']

# In development, emails print to the terminal instead of sending
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'