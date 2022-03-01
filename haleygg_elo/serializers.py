from rest_framework import serializers


class EloRankingSerializer(serializers.Serializer):
    name = serializers.CharField()
    current_elo = serializers.DecimalField(max_digits=6, decimal_places=1)


class EloHistorySerializer(serializers.Serializer):
    elo = serializers.DecimalField(max_digits=6, decimal_places=1)
    date = serializers.DateField()
