from rest_framework.viewsets import ModelViewSet

from server.models import League
from server.serializers import LeagueSerializer


class LeagueViewSet(ModelViewSet):
    serializer_class = LeagueSerializer
    queryset = League.objects.all()
