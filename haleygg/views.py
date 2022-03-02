from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from haleygg.mixins import MatchFilterMixin
from haleygg.models import League
from haleygg.models import Map
from haleygg.models import Match
from haleygg.models import Player
from haleygg.serializers import MapSerializer
from haleygg.serializers import MatchSerializer
from haleygg.serializers import LeagueSerializer
from haleygg.serializers import PlayerMatchSummarySerializer
from haleygg.serializers import PlayerSerializer
from haleygg.serializers import WinRatioByRaceSerializer
from haleygg_elo.models import update_all_elo_related_with_league


class LeagueViewSet(ModelViewSet):
    serializer_class = LeagueSerializer
    queryset = League.objects.all()


class PlayerViewSet(ModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()
    lookup_field = "name"


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

    def perform_destroy(self, instance):
        league = instance.league
        is_melee_match = instance.player_tuples.count() == 1
        instance.delete()
        if is_melee_match and league.is_elo_rating_active:
            update_all_elo_related_with_league(league)


class MatchSummaryView(MatchFilterMixin, GenericAPIView):
    serializer_class = WinRatioByRaceSerializer
    queryset = (
        Match.statistics.select_related("league", "map")
        .prefetch_related("player_tuples")
        .all()
    )

    def get_serializer_class(self):
        if self.player:
            return PlayerMatchSummarySerializer
        return self.serializer_class

    def get(self, request, *args, **kwargs):
        queryset = self.aggregate_queryset()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance=queryset)
        return Response(serializer.data)

    def aggregate_queryset(self):
        queryset = self.filter_queryset(self.get_queryset())
        self.player = self.request.query_params.get("player")
        if self.player:
            return queryset.get_player_statistics(self.player)
        else:
            return queryset.get_win_ratio_by_race()
