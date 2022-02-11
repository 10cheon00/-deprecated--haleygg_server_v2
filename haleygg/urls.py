from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from haleygg.views import MatchSummaryView
from haleygg.views import MatchViewSet
from haleygg.views import MapViewSet
from haleygg.views import LeagueViewSet
from haleygg.views import ProfileViewSet


router = DefaultRouter()
router.register(r"maps", MapViewSet)
router.register(r"matches", MatchViewSet)
router.register(r"leagues", LeagueViewSet)
router.register(r"profiles", ProfileViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("matches-summary/", MatchSummaryView.as_view()),
]