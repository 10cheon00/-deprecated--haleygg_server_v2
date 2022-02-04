import os

from haleygg_server.settings.base import *


ALLOWED_HOSTS += ["127.0.0.1"]

INSTALLED_APPS += [
    "debug_toolbar",
    "server",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

DEBUG = True

STATICFILES_DIRS = (os.path.join("static"),)
