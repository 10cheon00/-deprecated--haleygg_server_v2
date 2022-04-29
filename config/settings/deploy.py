from config.settings.base import *


ALLOWED_HOSTS = ["haleygg.10cheon00.xyz"]

WSGI_APPLICATION = "config.wsgi.deploy.application"


# CORS

CORS_ORIGIN_WHITELIST = ["https://www.haleygg.kr"]
