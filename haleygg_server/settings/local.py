from haleygg_server.settings.base import *

# CORS

# CORS_ORIGIN_WHITELIST = ["http://127.0.0.1:8000"]

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True


ALLOWED_HOSTS += ["127.0.0.1"]

INSTALLED_APPS += [
    "debug_toolbar",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

DEBUG = True
