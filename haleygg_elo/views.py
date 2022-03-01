from rest_framework.views import APIView
from rest_framework.response import Response

from haleygg_elo.models import get_elo_history_of_player
from haleygg_elo.models import get_elo_ranking
from haleygg_elo.serializers import EloHistorySerializer
from haleygg_elo.serializers import EloRankingSerializer


class EloRankingView(APIView):
    def get(self, request, *args, **kwargs):
        league = request.query_params.get("league")
        ranking_queryset = get_elo_ranking(league=league)
        serializer = EloRankingSerializer(instance=ranking_queryset, many=True)
        return Response(serializer.data)


class EloHistoryView(APIView):
    def get(self, request, *args, **kwargs):
        league = request.query_params.get("league")
        player = request.query_params.get("player")
        history_queryset = get_elo_history_of_player(league=league, player=player)
        serializer = EloHistorySerializer(instance=history_queryset, many=True)
        return Response(serializer.data)
