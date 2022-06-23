from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from haleygg.views import MatchSummaryView
from haleygg.views import MatchViewSet
from haleygg.views import MapViewSet
from haleygg.views import LeagueViewSet
from haleygg.views import PlayerViewSet
from haleygg.views import PlayerRankView
from haleygg.views import PlayerComparisonView


router = DefaultRouter()
router.register(r"maps", MapViewSet)
router.register(r"matches", MatchViewSet)
router.register(r"leagues", LeagueViewSet)
router.register(r"players", PlayerViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("matches-summary/", MatchSummaryView.as_view(), name="matches-summary"),
    path("ranks/", PlayerRankView.as_view(), name="ranks"),
    path("compare/", PlayerComparisonView.as_view(), name="comparison"),
]
