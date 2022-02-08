from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from server.views import MatchSummaryView
from server.views import MatchViewSet
from server.views import MapViewSet
from server.views import LeagueViewSet
from server.views import ProfileViewSet


router = DefaultRouter()
router.register(r"maps", MapViewSet)
router.register(r"matches", MatchViewSet)
router.register(r"leagues", LeagueViewSet)
router.register(r"profiles", ProfileViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("matches-summary/", MatchSummaryView.as_view()),
]
