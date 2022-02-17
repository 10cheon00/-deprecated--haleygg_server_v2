from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

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
        extra_kwargs = {"name": {"required": True}, "image": {"required": True}}


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "name", "favorate_race", "joined_date", "career"]


class PlayerListSerializer(serializers.ListSerializer):
    def validate(self, players):
        error_msg = {}

        players_count = len(players)

        if players_count % 2 == 1:
            error_msg["players_count"] = "플레이어의 수는 짝수여야 합니다."

        profiles = []
        winners_count = 0
        for player in players:
            profile = player.get("profile")
            if profile in profiles:
                if not error_msg.get("profile"):
                    error_msg["profile"] = []
                error_msg["profile"].append(f"플레이어 {profile}가 중복되었습니다.")

            profiles.append(profile)

            winners_count += player.get("win_state")

        if winners_count * 2 != players_count:
            error_msg["win_state"] = "승리한 플레이어의 수는 전체 플레이어 수의 절반이어야 합니다."

        if error_msg:
            raise serializers.ValidationError(error_msg)

        return players

    def create(self, validated_data, match):
        opponent = None
        if len(validated_data) > 2:
            return validated_data

        player = Player(
            match=match,
            profile=validated_data[0].get("profile"),
            win_state=validated_data[0].get("win_state"),
            race=validated_data[0].get("race"),
        )
        opponent = Player(
            match=match,
            profile=validated_data[1].get("profile"),
            win_state=validated_data[1].get("win_state"),
            race=validated_data[1].get("race"),
            opponent=player,
        )
        player.save()
        opponent.save()
        player.opponent = opponent
        player.save()

    def update(self, instance, validated_data):
        self.player_mapping = {player.id: player for player in instance}
        data_mapping = {data.get("id"): data for data in validated_data}

        different_ids = set(self.player_mapping.keys() - data_mapping.keys())
        if different_ids:
            raise serializers.ValidationError(
                {"players_id": f"{different_ids}에 해당하는 값이 없습니다."}
            )

        for player_id, data in data_mapping.items():
            player_instance = self.find_player_instance(player_id)
            player_instance.profile = data.get("profile")
            player_instance.race = data.get("race")
            player_instance.win_state = data.get("win_state")

        Player.objects.bulk_update(instance, ["profile", "race", "win_state"])

        return instance

    def find_player_instance(self, player_id):
        return self.player_mapping[player_id]


class PlayerSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(), required=True
    )
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Player
        fields = ["id", "profile", "race", "win_state"]
        extra_kwargs = {
            "id": {"read_only": True},
            "race": {"required": True},
            "win_state": {"required": True},
        }
        list_serializer_class = PlayerListSerializer


class MatchSerializer(serializers.ModelSerializer):
    league = serializers.PrimaryKeyRelatedField(
        queryset=League.objects.all(), required=True
    )
    map = serializers.PrimaryKeyRelatedField(queryset=Map.objects.all(), required=True)
    players = PlayerSerializer(
        many=True,
        required=True,
        allow_empty=False,
        min_length=2,
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
            self.create_players()
        return self.match

    def update(self, instance, validated_data):
        player_validated_data = validated_data.pop("players")
        player_instances = instance.get_related_players()
        player_serializer = PlayerSerializer(many=True)

        with transaction.atomic():
            player_serializer.update(
                instance=player_instances, validated_data=player_validated_data
            )
            if validated_data["is_melee_match"]:
                if instance.get_related_players().count() == 2:
                    validated_data["is_melee_match"] = True
                else:
                    validated_data["is_melee_match"] = False

            return super().update(instance=instance, validated_data=validated_data)

    def get_data_from_validated_data(self, validated_data):
        self.league = validated_data.get("league")
        self.map = validated_data.get("map")
        self.date = validated_data.get("date")
        self.title = validated_data.get("title")
        self.miscellaneous = validated_data.get("miscellaneous")
        self.players = validated_data.pop("players")
        self.is_melee_match = True if len(self.players) == 2 else False

    def create_match(self):
        self.match = Match.objects.create(
            league=self.league,
            date=self.date,
            title=self.title,
            map=self.map,
            miscellaneous=self.miscellaneous,
            is_melee_match=self.is_melee_match,
        )

    def create_players(self):
        player_serializer = PlayerSerializer(many=True)
        player_serializer.create(validated_data=self.players, match=self.match)


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
