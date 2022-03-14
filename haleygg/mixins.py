from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import ModelMultipleChoiceFilter

from haleygg.models import Match
from haleygg.models import Player


class MatchFilterSet(FilterSet):
    players = ModelMultipleChoiceFilter(
        field_name="player_tuples", method="get_player", queryset=Player.objects.all()
    )

    class Meta:
        model = Match
        fields = ["league", "map", "players"]

    def get_player(self, queryset, name, value, *args, **kwargs):
        for player in value:
            queryset = queryset.filter(
                Q(player_tuples__winner=player) | Q(player_tuples__loser=player)
            )

        return queryset


class MatchFilterMixin(object):
    filter_backends = [
        DjangoFilterBackend,
    ]
    filter_class = MatchFilterSet
