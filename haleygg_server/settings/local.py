import os

from haleygg_server.settings.base import *


ALLOWED_HOSTS += ["127.0.0.1"]

INSTALLED_APPS += [
    "debug_toolbar",
    "haleygg",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

DEBUG = True

STATIC_ROOT = ""

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR),
]
