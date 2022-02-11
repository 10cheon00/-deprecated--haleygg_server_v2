from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import ModelMultipleChoiceFilter

from haleygg.models import Match
from haleygg.models import Profile


class MatchFilterSet(FilterSet):
    profile = ModelMultipleChoiceFilter(
        field_name="players__profile",
        to_field_name="id",
        queryset=Profile.objects.all(),
        conjoined=True,
    )

    class Meta:
        model = Match
        fields = ["league", "map", "profile", "is_melee_match"]


class MatchFilterMixin(object):
    filter_backends = [
        DjangoFilterBackend,
    ]
    filter_class = MatchFilterSet
