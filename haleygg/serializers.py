from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from haleygg.models import League
from haleygg.models import Match
from haleygg.models import Map
from haleygg.models import PlayerTuple
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
        extra_kwargs = {"name": {"required": True}, "image": {"required": True}}


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "name", "favorate_race", "joined_date", "career"]


class PlayerListSerializer(serializers.ListSerializer):
    def validate(self, player_tuples):
        self.error_msg = []

        profiles = []
        for player_tuple in player_tuples:
            winner = player_tuple.get("winner")
            if winner in profiles:
                self.error_msg.append(f"플레이어 {winner}가 중복되었습니다.")
            profiles.append(winner)

            loser = player_tuple.get("loser")
            if loser in profiles:
                self.error_msg.append(f"플레이어 {loser}가 중복되었습니다.")
            profiles.append(loser)

        if self.error_msg:
            raise serializers.ValidationError(self.error_msg)

        return player_tuples

    def create(self, validated_data, match):
        player_tuples = [PlayerTuple(match=match, **item) for item in validated_data]
        PlayerTuple.objects.bulk_create(player_tuples)
        return player_tuples

    def update(self, instance, validated_data):
        self.player_tuple_mapping = {
            player_tuple.id: player_tuple for player_tuple in instance
        }
        data_mapping = {data.get("id"): data for data in validated_data}

        different_ids = set(self.player_tuple_mapping.keys() - data_mapping.keys())
        if different_ids:
            raise serializers.ValidationError(
                {"player_tuples_id": f"{different_ids}에 해당하는 값이 없습니다."}
            )

        for player_id, data in data_mapping.items():
            player_instance = self.find_player_instance(player_id)
            player_instance.winner = data.get("winner")
            player_instance.winner_race = data.get("winner_race")
            player_instance.loser = data.get("loser")
            player_instance.loser_race = data.get("loser_race")

        PlayerTuple.objects.bulk_update(
            instance, ["winner", "winner_race", "loser", "loser_race"]
        )

        return instance

    def find_player_instance(self, player_id):
        return self.player_tuple_mapping[player_id]


class PlayerTupleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerTuple
        fields = [
            "id",
            "winner",
            "winner_race",
            "loser",
            "loser_race",
        ]
        extra_kwargs = {
            "id": {"read_only": False},
            "winner_race": {"required": True},
            "loser_race": {"required": True},
        }
        list_serializer_class = PlayerListSerializer


class MatchSerializer(serializers.ModelSerializer):
    league = serializers.PrimaryKeyRelatedField(
        queryset=League.objects.all(), required=True
    )
    map = serializers.PrimaryKeyRelatedField(queryset=Map.objects.all(), required=True)
    player_tuples = PlayerTupleSerializer(many=True, required=True, allow_empty=False)

    class Meta:
        model = Match
        fields = [
            "id",
            "league",
            "date",
            "title",
            "map",
            "miscellaneous",
            "player_tuples",
        ]
        extra_kwargs = {
            "date": {"required": True},
            "title": {"required": True},
        }
        validators = [
            UniqueTogetherValidator(
                queryset=Match.objects.all(), fields=["league", "title"]
            ),
        ]

    def create(self, validated_data):
        self.get_data_from_validated_data(validated_data=validated_data)

        with transaction.atomic():
            self.create_match()
            self.create_player_tuples()
        return self.match

    def update(self, instance, validated_data):
        player_validated_data = validated_data.pop("player_tuples")
        player_instances = instance.get_related_player_tuples()
        player_serializer = PlayerTupleSerializer(many=True)

        with transaction.atomic():
            player_serializer.update(
                instance=player_instances, validated_data=player_validated_data
            )
            return super().update(instance=instance, validated_data=validated_data)

    def get_data_from_validated_data(self, validated_data):
        self.league = validated_data.get("league")
        self.map = validated_data.get("map")
        self.date = validated_data.get("date")
        self.title = validated_data.get("title")
        self.miscellaneous = validated_data.get("miscellaneous")
        self.player_tuples = validated_data.pop("player_tuples")

    def create_match(self):
        self.match = Match.objects.create(
            league=self.league,
            date=self.date,
            title=self.title,
            map=self.map,
            miscellaneous=self.miscellaneous,
        )

    def create_player_tuples(self):
        player_serializer = PlayerTupleSerializer(many=True)
        player_serializer.create(validated_data=self.player_tuples, match=self.match)


class WinRatioByRaceSerializer(serializers.Serializer):
    protoss_wins_to_terran_count = serializers.IntegerField()
    protoss_wins_to_zerg_count = serializers.IntegerField()
    terran_wins_to_protoss_count = serializers.IntegerField()
    terran_wins_to_zerg_count = serializers.IntegerField()
    zerg_wins_to_protoss_count = serializers.IntegerField()
    zerg_wins_to_terran_count = serializers.IntegerField()


class PlayerMatchSummarySerializer(WinRatioByRaceSerializer):
    protoss_loses_to_terran_count = serializers.IntegerField()
    protoss_loses_to_zerg_count = serializers.IntegerField()
    terran_loses_to_protoss_count = serializers.IntegerField()
    terran_loses_to_zerg_count = serializers.IntegerField()
    zerg_loses_to_protoss_count = serializers.IntegerField()
    zerg_loses_to_terran_count = serializers.IntegerField()

    winning_melee_matches_count = serializers.IntegerField()
    losing_melee_matches_count = serializers.IntegerField()
    winning_top_and_bottom_matches_count = serializers.IntegerField()
    losing_top_and_bottom_matches_count = serializers.IntegerField()
