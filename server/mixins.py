from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import ModelMultipleChoiceFilter

from server.models import Match
from server.models import Profile


class MatchFilterSet(FilterSet):
    profiles = ModelMultipleChoiceFilter(
        field_name="players__profile",
        to_field_name="id",
        queryset=Profile.objects.all(),
        conjoined=True,
    )

    class Meta:
        model = Match
        fields = ["league", "map", "is_melee_match", "profiles"]


class MatchFilterMixin(object):
    filter_backends = [
        DjangoFilterBackend,
    ]
    filter_class = MatchFilterSet
