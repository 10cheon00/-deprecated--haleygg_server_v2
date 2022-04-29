from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import ModelChoiceFilter
from django_filters.rest_framework import ModelMultipleChoiceFilter

from haleygg.models import League
from haleygg.models import Map
from haleygg.models import Match
from haleygg.models import Player


class LeagueFilterSet(FilterSet):
    class Meta:
        model = League
        fields = [
            "type",
        ]


class LeagueFilterMixin(object):
    filter_backends = [DjangoFilterBackend]
    filter_class = LeagueFilterSet


class MapFilterSet(FilterSet):
    class Meta:
        model = Map
        fields = [
            "type",
        ]


class MapFilterMixin(object):
    filter_backends = [DjangoFilterBackend]
    filter_class = MapFilterSet


class MatchFilterSet(FilterSet):
    league = ModelChoiceFilter(queryset=League.objects.all(), to_field_name="name")
    map = ModelChoiceFilter(queryset=Map.objects.all(), to_field_name="name")
    players = ModelMultipleChoiceFilter(
        method="get_player",
        field_name="player_tuples",
        queryset=Player.objects.all(),
        to_field_name="name",
    )

    class Meta:
        model = Match
        fields = ["league", "map", "players", "league__type"]

    def get_player(self, queryset, name, value):
        for player in value:
            queryset = queryset.filter(
                Q(player_tuples__winner__name=player.name)
                | Q(player_tuples__loser__name=player.name)
            )

        return queryset


class MatchFilterMixin(object):
    filter_backends = [
        DjangoFilterBackend,
    ]
    filter_class = MatchFilterSet
