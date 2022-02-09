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
        fields = ["id", "name", "image_url"]
        extra_kwargs = {"name": {"required": True}, "image_url": {"required": False}}


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "name", "favorate_race", "joined_date", "career"]
        extra_kwargs = {
            "name": {"required": True},
            "favorate_race": {"required": True},
            "joined_date": {"required": True},
        }


class PlayerListSerializer(serializers.ListSerializer):
    def create(self, validated_data, match):
        opponent = None
        for player in validated_data:
            new_player = Player.objects.create(
                match=match,
                profile=player.get("profile"),
                win_state=player.get("win_state"),
                race=player.get("race"),
            )
            if opponent:
                if opponent.profile is new_player.profile:
                    raise exceptions.ValidationError(detail="잘못된 플레이어를 입력했습니다.")
                new_player.opponent = opponent
                opponent.opponent = new_player
                new_player.save()
                opponent.save()
                opponent = None
            else:
                opponent = new_player

    def update(self, instance, validated_data):
        player_mapping = {player.id: player for player in instance}
        data_mapping = {data.get("id"): data for data in validated_data}

        player_objects = []
        try:
            # TODO
            # 최적화쿼리 필요
            # 게임 상대 참조 예외처리
            for player_id, data in data_mapping.items():
                player_instance = player_mapping.get(player_id)
                player_instance.profile = data["profile"]
                player_instance.race = data.get("race")
                player_instance.win_state = data.get("win_state")

                player_instance.save()
                player_objects.append(player_instance)
        except AttributeError:
            raise exceptions.ValidationError(detail="잘못된 플레이어를 입력했습니다.")
        return player_objects


class PlayerSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(), required=True
    )

    class Meta:
        model = Player
        fields = ["id", "profile", "race", "win_state"]
        extra_kwargs = {
            "id": {"read_only": False},
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
        extra_kwargs = {"date": {"required": True}, "title": {"required": True}}

    def create(self, validated_data):
        self.get_data_from_validated_data(validated_data=validated_data)
        self.check_match_already_exists()

        with transaction.atomic():
            self.create_match()
            self.create_players()
        return self.match

    def update(self, instance, validated_data):
        player_validated_data = validated_data.pop("players")
        player_instances = instance.players.all()
        player_serializer = PlayerSerializer(many=True)

        with transaction.atomic():
            player_serializer.update(
                instance=player_instances, validated_data=player_validated_data
            )
            self.title = validated_data.get("title")
            self.league = validated_data.get("league")
            if instance.league != self.league or instance.title != self.title:
                self.check_match_already_exists()
            return super().update(instance=instance, validated_data=validated_data)

    def get_data_from_validated_data(self, validated_data):
        self.league = validated_data.get("league")
        self.map = validated_data.get("map")
        self.date = validated_data.get("date")
        self.title = validated_data.get("title")
        self.miscellaneous = validated_data.get("miscellaneous")
        self.is_melee_match = True if len(validated_data.get("players")) > 2 else False
        self.players = validated_data.pop("players")

    def check_match_already_exists(self):
        if Match.objects.filter(
            league=self.league.id, title__iexact=self.title
        ).exists():
            raise exceptions.ParseError(detail="이미 있는 전적입니다.")

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
