from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from haleygg.mixins import MapFilterMixin
from haleygg.mixins import MatchFilterMixin
from haleygg.models import League
from haleygg.models import Map
from haleygg.models import Match
from haleygg.models import Player
from haleygg.serializers import MapSerializer
from haleygg.serializers import MapStatisticsSerializer
from haleygg.serializers import MatchSerializer
from haleygg.serializers import LeagueSerializer
from haleygg.serializers import PlayerMatchSummarySerializer
from haleygg.serializers import PlayerSerializer
from haleygg.serializers import WinRatioByRaceSerializer
from haleygg_elo.models import update_all_elo_related_with_league


class LeagueViewSet(ModelViewSet):
    serializer_class = LeagueSerializer
    queryset = League.objects.all()

    def list(self, request, *args, **kwargs):
        is_elo_rating_active = request.query_params.get("is_elo_rating_active")
        if is_elo_rating_active:
            queryset = League.objects.filter(is_elo_rating_active=is_elo_rating_active)
        else:
            queryset = League.objects.all()
        serializer = self.get_serializer(instance=queryset, many=True)
        return Response(serializer.data)


class PlayerViewSet(ModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()
    lookup_field = "name__iexact"


class MapViewSet(MapFilterMixin, ModelViewSet):
    serializer_class = MapSerializer
    queryset = Map.objects.all()


class MatchPagination(PageNumberPagination):
    page_size = 10


class MatchViewSet(MatchFilterMixin, ModelViewSet):
    serializer_class = MatchSerializer
    queryset = (
        Match.objects.select_related("league", "map")
        .prefetch_related("player_tuples")
        .all()
    )
    pagination_class = MatchPagination

    def perform_destroy(self, instance):
        league = instance.league
        is_melee_match = instance.player_tuples.count() == 1
        instance.delete()
        if is_melee_match and league.is_elo_rating_active:
            update_all_elo_related_with_league(league)

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        if not is_many:
            return super().create(request=request, args=args, kwargs=kwargs)

        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().reverse())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MatchSummaryView(MatchFilterMixin, GenericAPIView):
    queryset = (
        Match.statistics.select_related("league", "map")
        .prefetch_related("player_tuples")
        .all()
    )

    def get_serializer_class(self):
        if self.player:
            return PlayerMatchSummarySerializer
        if self.map:
            return MapStatisticsSerializer

        return WinRatioByRaceSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.aggregate_queryset()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance=queryset)
        return Response(serializer.data)

    def aggregate_queryset(self):
        queryset = self.filter_queryset(self.get_queryset())

        self.player = self.request.query_params.get("player")
        self.map = self.request.query_params.get("map")

        if self.player:
            return queryset.get_player_statistics(self.player)
        elif self.map:
            return queryset.get_map_statistics(self.map)
        else:
            return queryset.get_win_ratio_by_race()
