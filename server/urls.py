from django.urls import path, include
from rest_framework.routers import DefaultRouter

from server.views import LeagueViewSet


router = DefaultRouter()
router.register(r"leagues", LeagueViewSet)

urlpatterns = [path("", include(router.urls))]
