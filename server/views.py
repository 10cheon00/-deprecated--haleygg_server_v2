from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ParseError
from rest_framework.viewsets import ModelViewSet

from server.models import League
from server.models import Map
from server.models import Match
from server.models import Profile
from server.serializers import MatchSerializer
from server.serializers import MapSerializer
from server.serializers import LeagueSerializer
from server.serializers import ProfileSerializer


class LeagueViewSet(ModelViewSet):
    serializer_class = LeagueSerializer
    queryset = League.objects.all()


class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()


class MapViewSet(ModelViewSet):
    serializer_class = MapSerializer
    queryset = Map.objects.all()


class MatchViewSet(ModelViewSet):
    serializer_class = MatchSerializer
    filter_backends = [
        DjangoFilterBackend,
    ]
    filter_fields = ("league", "map", "is_melee_match")
    queryset = (
        Match.objects.select_related("league", "map")
        .prefetch_related("players", "players__profile")
        .all()
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        profiles = self.query_params.getlist("profiles[]", None)
        if profiles:
            try:
                filtered_queryset = queryset
                for profile in profiles:
                    filtered_queryset = filtered_queryset.filter(
                        players__profile=profile
                    )
                queryset = filtered_queryset
            except ValueError:
                pass

        return queryset

    def list(self, request, *args, **kwargs):
        self.query_params = request.query_params
        return super().list(request=request, args=args, kwargs=kwargs)
