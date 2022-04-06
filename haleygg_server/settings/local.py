from haleygg_server.settings.base import *


ALLOWED_HOSTS += ["127.0.0.1"]

DEBUG = True

INSTALLED_APPS += [
    "debug_toolbar",
]

WSGI_APPLICATION = "haleygg_server.wsgi.local.application"


# REST_FRAMEWORK

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
}


# CORS

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True

# DEBUG TOOLBAR

INTERNAL_IPS = [
    "127.0.0.1",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
