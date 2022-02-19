from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import ModelMultipleChoiceFilter

from haleygg.models import Match
from haleygg.models import Profile


class MatchFilterSet(FilterSet):
    profiles = ModelMultipleChoiceFilter(
        field_name="player_tuples",
        method="get_profile",
        queryset=Match.objects.prefetch_related("player_tuples"),
    )

    class Meta:
        model = Match
        fields = ["league", "map", "profiles"]

    def get_profile(self, queryset, name, value, *args, **kwargs):
        # TODO
        # not properly works...
        return queryset.filter()


class MatchFilterMixin(object):
    filter_backends = [
        DjangoFilterBackend,
    ]
    filter_class = MatchFilterSet
