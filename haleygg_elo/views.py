from rest_framework.views import APIView
from rest_framework.response import Response

from haleygg_elo.models import get_elo_history_of_player
from haleygg_elo.models import get_elo_ranking
from haleygg_elo.serializers import EloHistorySerializer
from haleygg_elo.serializers import EloRankingSerializer


class EloRankingView(APIView):
    def get(self, request, *args, **kwargs):
        league_name = request.query_params.get("league")
        ranking_queryset = get_elo_ranking(league_name=league_name)
        serializer = EloRankingSerializer(instance=ranking_queryset, many=True)
        return Response(serializer.data)


class EloHistoryView(APIView):
    def get(self, request, *args, **kwargs):
        league_name = request.query_params.get("league")
        player_name = request.query_params.get("player")
        history_queryset = get_elo_history_of_player(
            league_name=league_name, player_name=player_name
        )
        serializer = EloHistorySerializer(instance=history_queryset, many=True)
        return Response(serializer.data)
