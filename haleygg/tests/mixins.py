from django.urls import include
from django.urls import path
from rest_framework.test import URLPatternsTestCase


class HaleyggUrlPatternsTestMixin(URLPatternsTestCase):
    urlpatterns = [path("api/", include("haleygg.urls"))]
