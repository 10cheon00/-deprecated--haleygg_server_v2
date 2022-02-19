from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import ModelMultipleChoiceFilter

from haleygg.models import Match
from haleygg.models import Profile


class MatchFilterSet(FilterSet):
    profiles = ModelMultipleChoiceFilter(
        field_name="player_tuples", method="get_profile", queryset=Profile.objects.all()
    )

    class Meta:
        model = Match
        fields = ["league", "map", "profiles"]

    def get_profile(self, queryset, name, value, *args, **kwargs):
        for profile in value:
            queryset = queryset.filter(
                Q(player_tuples__winner=profile) | Q(player_tuples__loser=profile)
            )

        return queryset


class MatchFilterMixin(object):
    filter_backends = [
        DjangoFilterBackend,
    ]
    filter_class = MatchFilterSet
