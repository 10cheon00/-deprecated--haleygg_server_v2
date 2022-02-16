from django.db.models import F
from rest_framework.response import Response
from rest_framework.views import APIView

from elo.models import Elo
from elo.serializers import EloRankingSerializer
from elo.serializers import PlayerEloSerializer


class EloRankingListView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Elo.ranking.get_ranking()
        serializer = EloRankingSerializer(instance=queryset, many=True)
        return Response(serializer.data)


class EloDetailView(APIView):
    def get(self, request, *args, **kwargs):
        profile = self.kwargs.get("profile")
        queryset = Elo.filter.get_queryset_related_profile(profile)
        serializer = PlayerEloSerializer(instance=queryset, many=True)
        return Response(serializer.data)
