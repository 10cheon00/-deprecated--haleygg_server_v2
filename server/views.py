from rest_framework.viewsets import ModelViewSet

from server.mixins import MatchFilterMixin
from server.models import League
from server.models import Map
from server.models import Match
from server.models import Profile
from server.serializers import MatchSerializer
from server.serializers import MapSerializer
from server.serializers import MatchSerializer
from server.serializers import LeagueSerializer
from server.serializers import ProfileSerializer


class LeagueViewSet(ModelViewSet):
    serializer_class = LeagueSerializer
    queryset = League.objects.all()


class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()


class MapViewSet(ModelViewSet):
    serializer_class = MapSerializer
    queryset = Map.objects.all()


class MatchViewSet(MatchFilterMixin, ModelViewSet):
    serializer_class = MatchSerializer
    queryset = (
        Match.objects.select_related("league", "map")
        .prefetch_related("players", "players__profile")
        .all()
    )
