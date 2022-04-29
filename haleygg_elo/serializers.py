from rest_framework import serializers

from haleygg.models import Player
from haleygg_elo.models import Elo


class EloHistorySerializer(serializers.Serializer):
    rating = serializers.DecimalField(max_digits=6, decimal_places=1)
    date = serializers.DateField()


class EloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Elo
        fields = ("player_tuple", "winner_rating", "loser_rating")


class EloRankingSerializer(serializers.ModelSerializer):
    current_elo = serializers.DecimalField(max_digits=6, decimal_places=1)
    # win_count = serializers.IntegerField()

    class Meta:
        model = Player
        fields = ["name", "favorate_race", "current_elo"]
