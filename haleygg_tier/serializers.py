from rest_framework import serializers

from haleygg.models import League
from haleygg.models import Player
from haleygg_tier.models import PlayerTier


class PlayerTierSerializer(serializers.ModelSerializer):
    league = serializers.SlugRelatedField(
        queryset=League.objects.all(), slug_field="name"
    )
    player = serializers.SlugRelatedField(
        queryset=Player.objects.all(), slug_field="name"
    )

    class Meta:
        model = PlayerTier
        fields = ("league", "player", "tier")
