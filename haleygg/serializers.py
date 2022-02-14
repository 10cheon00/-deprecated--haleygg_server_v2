from django.db import transaction
from rest_framework import serializers
from rest_framework import exceptions

from haleygg.models import League
from haleygg.models import Match
from haleygg.models import Map
from haleygg.models import Player
from haleygg.models import Profile


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = ["id", "name"]
        extra_kwargs = {"name": {"required": True}}


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = ["id", "name", "image"]
        extra_kwargs = {"name": {"required": True}, "image": {"required": False}}


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "name", "favorate_race", "joined_date", "career"]


class PlayerSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(), required=True
    )

    class Meta:
        model = Player
        fields = ["id", "profile", "race", "win_state"]


class MatchSerializer(serializers.ModelSerializer):
    league = serializers.PrimaryKeyRelatedField(
        queryset=League.objects.all(), required=True
    )
    map = serializers.PrimaryKeyRelatedField(queryset=Map.objects.all(), required=True)
    players = PlayerSerializer(
        many=True, required=True, allow_empty=False, min_length=2
    )

    class Meta:
        model = Match
        fields = [
            "id",
            "league",
            "date",
            "title",
            "map",
            "miscellaneous",
            "is_melee_match",
            "players",
        ]


class WinRatioByRaceSerializer(serializers.Serializer):
    protoss_wins_to_terran_count = serializers.IntegerField()
    protoss_wins_to_zerg_count = serializers.IntegerField()
    terran_wins_to_protoss_count = serializers.IntegerField()
    terran_wins_to_zerg_count = serializers.IntegerField()
    zerg_wins_to_protoss_count = serializers.IntegerField()
    zerg_wins_to_terran_count = serializers.IntegerField()
    protoss_loses_to_terran_count = serializers.IntegerField()
    protoss_loses_to_zerg_count = serializers.IntegerField()
    terran_loses_to_protoss_count = serializers.IntegerField()
    terran_loses_to_zerg_count = serializers.IntegerField()
    zerg_loses_to_protoss_count = serializers.IntegerField()
    zerg_loses_to_terran_count = serializers.IntegerField()


class PlayerMatchSummarySerializer(WinRatioByRaceSerializer):
    melee_winning_count = serializers.IntegerField()
    melee_losing_count = serializers.IntegerField()
    top_and_bottom_winning_count = serializers.IntegerField()
    top_and_bottom_losing_count = serializers.IntegerField()
