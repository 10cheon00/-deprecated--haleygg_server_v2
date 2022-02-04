from django.db import IntegrityError
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet

from server.models import League
from server.models import Map
from server.models import Match
from server.models import Player
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


class MatchViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
