from rest_framework import serializers

from haleygg.models import Player


class EloRankingSerializer(serializers.ModelSerializer):
    current_elo = serializers.DecimalField(max_digits=6, decimal_places=1)
    # win_count = serializers.IntegerField()

    class Meta:
        model = Player
        fields = ["name", "favorate_race", "current_elo"]


class EloHistorySerializer(serializers.Serializer):
    elo = serializers.DecimalField(max_digits=6, decimal_places=1)
    date = serializers.DateField()
