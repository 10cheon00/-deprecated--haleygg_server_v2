from django.db.models import Count
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models import Subquery
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import ChoiceFilter
from django_filters.rest_framework import ModelChoiceFilter
from django_filters.rest_framework import ModelMultipleChoiceFilter

from haleygg.models import League
from haleygg.models import Map
from haleygg.models import Match
from haleygg.models import Player
from haleygg.models import PlayerTuple


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
    MATCH_TYPE_CHOICES = (
        ("melee", "melee"),
        ("top_and_bottom", "top_and_bottom"),
    )

    league = ModelChoiceFilter(queryset=League.objects.all(), to_field_name="name")
    map = ModelChoiceFilter(queryset=Map.objects.all(), to_field_name="name")
    players = ModelMultipleChoiceFilter(
        method="get_player",
        field_name="player_tuples",
        queryset=Player.objects.all(),
        to_field_name="name",
    )
    match_type = ChoiceFilter(
        choices=MATCH_TYPE_CHOICES,
        field_name="Match type",
        method="get_filtered_matches_by_match_type",
    )

    class Meta:
        model = Match
        fields = ["league", "map", "players", "league__type", "match_type"]

    def get_player(self, queryset, name, value):
        for player in value:
            queryset = queryset.filter(
                Q(player_tuples__winner__name=player.name)
                | Q(player_tuples__loser__name=player.name)
            )

        return queryset

    def get_filtered_matches_by_match_type(self, queryset, field_name, value):
        if value == "melee":
            queryset = queryset.annotate(
                player_tuples_count=Subquery(
                    Match.objects.filter(id=OuterRef("id"))
                    .annotate(Count("player_tuples"))
                    .values("player_tuples__count")
                )
            ).filter(player_tuples_count=1)
        elif value == "top_and_bottom":
            queryset = queryset.annotate(
                player_tuples_count=Subquery(
                    Match.objects.filter(id=OuterRef("id"))
                    .annotate(Count("player_tuples"))
                    .values("player_tuples__count")
                )
            ).filter(player_tuples_count__gt=1)
        return queryset


class MatchFilterMixin(object):
    filter_backends = [
        DjangoFilterBackend,
    ]
    filter_class = MatchFilterSet
