from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from haleygg_elo.models import Elo
from haleygg_elo.models import get_elo_history_of_player
from haleygg_elo.models import get_elo_ranking
from haleygg_elo.models import create_total_elo_data
from haleygg_elo.serializers import EloHistorySerializer
from haleygg_elo.serializers import EloRankingSerializer
from haleygg_elo.serializers import EloSerializer


class EloPagination(PageNumberPagination):
    page_size = 10


class EloListView(ListAPIView):
    serializer_class = EloSerializer
    queryset = Elo.objects.select_related(
        "player_tuple",
        "player_tuple__match",
        "player_tuple__winner",
        "player_tuple__loser",
    ).all()
    pagination_class = EloPagination

    def list(self, request, *args, **kwargs):
        league_type = request.query_params.get("league__type")
        player_name = request.query_params.get("players")

        if league_type is None or player_name is None:
            return super().list(request=request)

        history_queryset = get_elo_history_of_player(
            league_type=league_type, player_name=player_name
        ).reverse()

        page = self.paginate_queryset(history_queryset)
        if page is not None:
            serializer = EloHistorySerializer(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = EloHistorySerializer(instance=history_queryset, many=True)
        return Response(serializer.data)


class EloRankingView(APIView):
    def get(self, request, *args, **kwargs):
        league_type = request.query_params.get("league__type")
        ranking_queryset = get_elo_ranking(league_type=league_type)
        serializer = EloRankingSerializer(instance=ranking_queryset, many=True)
        return Response(serializer.data)


class EloUpdateView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        try:
            with transaction.atomic():
                Elo.objects.all().delete()
                create_total_elo_data(league_type="proleague")
                create_total_elo_data(league_type="starleague")
        except Exception as e:
            raise e
        return Response(status=status.HTTP_200_OK)
