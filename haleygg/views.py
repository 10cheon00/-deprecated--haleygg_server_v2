from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from haleygg.mixins import MatchFilterMixin
from haleygg.models import League
from haleygg.models import Map
from haleygg.models import Match
from haleygg.models import Profile
from haleygg.serializers import MapSerializer
from haleygg.serializers import MatchSerializer
from haleygg.serializers import LeagueSerializer
from haleygg.serializers import PlayerMatchSummarySerializer
from haleygg.serializers import ProfileSerializer
from haleygg.serializers import WinRatioByRaceSerializer


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
        .prefetch_related("player_tuples")
        .all()
    )


class MatchSummaryView(MatchFilterMixin, GenericAPIView):
    serializer_class = WinRatioByRaceSerializer
    queryset = (
        Match.statistics.select_related("league", "map")
        .prefetch_related("player_tuples")
        .all()
    )

    def get_serializer_class(self):
        if self.profile:
            return PlayerMatchSummarySerializer
        return self.serializer_class

    def get(self, request, *args, **kwargs):
        queryset = self.aggregate_queryset()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance=queryset)
        return Response(serializer.data)

    def aggregate_queryset(self):
        queryset = self.filter_queryset(self.get_queryset())
        self.profile = self.request.query_params.get("profile")
        if self.profile:
            return queryset.get_player_statistics(self.profile)
        else:
            return queryset.get_win_ratio_by_race()
