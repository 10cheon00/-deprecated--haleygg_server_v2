from rest_framework import serializers

from server.models import League


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = ["id", "name"]
