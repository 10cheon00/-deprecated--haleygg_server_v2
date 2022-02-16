from rest_framework import serializers

from elo.models import Elo


class EloRankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Elo
        fields = ["name", "value"]


class PlayerEloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Elo
        fields = ["value", "date"]
