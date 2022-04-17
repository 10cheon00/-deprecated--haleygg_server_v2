from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
from django.utils.encoding import smart_text

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from haleygg.models import League
from haleygg.models import Map
from haleygg.models import Match
from haleygg.models import Player
from haleygg.models import PlayerTuple
from haleygg_elo.models import create_elo
from haleygg_elo.models import update_all_elo_related_with_league


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = ["id", "name", "k_factor", "is_elo_rating_active"]
        extra_kwargs = {
            "name": {"required": True},
            "k_factor": {"required": False},
            "is_elo_rating_active": {"required": False},
        }


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = ["id", "name", "image", "type"]


class PlayerSerializer(serializers.ModelSerializer):
    joined_date = serializers.DateField(default=timezone.now().date)

    class Meta:
        model = Player
        fields = ["id", "name", "favorate_race", "joined_date", "career"]
        extra_kwargs = {
            "joined_date": {"required": False},
            "career": {"required": False},
        }


class PlayerTupleListSerializer(serializers.ListSerializer):
    def validate(self, player_tuples):
        error_msg = []

        is_melee_match = len(player_tuples) == 1

        if is_melee_match:
            if not player_tuples[0]["winner_race"]:
                error_msg.append({"winner_race": "개인전은 플레이어의 종족값이 필요합니다."})
            if not player_tuples[0]["loser_race"]:
                error_msg.append({"loser_race": "개인전은 플레이어의 종족값이 필요합니다."})

        players = []
        for player_tuple in player_tuples:
            winner_name = player_tuple.get("winner").name

            if not Player.objects.filter(name__iexact=winner_name).exists():
                error_msg.append({"winner": f"플레이어 {winner_name}은 존재하지 않습니다."})
            else:
                if winner_name in players:
                    error_msg.append({"winner": f"플레이어 {winner_name}가 중복되었습니다."})
                players.append(winner_name)

            loser_name = player_tuple.get("loser").name

            if not Player.objects.filter(name__iexact=loser_name).exists():
                error_msg.append({"loser": f"플레이어 {loser_name}은 존재하지 않습니다."})
            else:
                if loser_name in players:
                    error_msg.append({"loser": f"플레이어 {loser_name}가 중복되었습니다."})
                players.append(loser_name)

        if error_msg:
            raise serializers.ValidationError(error_msg)

        return player_tuples

    def create(self, validated_data, match):
        player_tuples = []
        for item in validated_data:
            player_tuples.append(
                PlayerTuple(
                    match=match,
                    winner=item["winner"],
                    loser=item["loser"],
                    winner_race=item.get("winner_race"),
                    loser_race=item.get("loser_race"),
                )
            )
        return PlayerTuple.objects.bulk_create(player_tuples)

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

        self.has_changed = False

        for player_id, data in data_mapping.items():
            player_tuple_instance = self.find_player_tuple_from_instance(player_id)
            if (
                player_tuple_instance.winner.name != data["winner"].name
                or player_tuple_instance.winner_race != data["winner_race"]
                or player_tuple_instance.loser.name != data["loser"].name
                or player_tuple_instance.loser_race != data["loser_race"]
            ):
                self.has_changed = True

            player_tuple_instance.winner = data["winner"]
            player_tuple_instance.winner_race = data["winner_race"]
            player_tuple_instance.loser = data["loser"]
            player_tuple_instance.loser_race = data["loser_race"]

        PlayerTuple.objects.bulk_update(
            instance, ["winner", "winner_race", "loser", "loser_race"]
        )

        return instance

    def find_player_tuple_from_instance(self, player_id):
        return self.player_tuple_mapping[player_id]


class CreatableSlugRelatedField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(
                **{f"{self.slug_field}__iexact": str(data)},
                defaults={self.slug_field: str(data)},
            )[0]
        except ObjectDoesNotExist:
            self.fail(
                "does_not_exist", slug_name=self.slug_field, value=smart_text(data)
            )
        except (TypeError, ValueError):
            self.fail("invalid")


class PlayerTupleSerializer(serializers.ModelSerializer):
    RACE_LIST = [
        ("P", "Protoss"),
        ("T", "Terran"),
        ("Z", "Zerg"),
        ("R", "Random"),
        ("", ""),
    ]

    winner = CreatableSlugRelatedField(queryset=Player.objects.all(), slug_field="name")
    loser = CreatableSlugRelatedField(queryset=Player.objects.all(), slug_field="name")
    winner_race = serializers.ChoiceField(
        allow_null=True, choices=RACE_LIST, default="", required=False
    )
    loser_race = serializers.ChoiceField(
        allow_null=True, choices=RACE_LIST, default="", required=False
    )

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
            "id": {"read_only": False, "required": False},
        }
        list_serializer_class = PlayerTupleListSerializer


class MatchListSerializer(serializers.ListSerializer):
    def validate(self, matches):
        match_names = []

        for match in matches:
            match_name = match["league"].name + match["title"]
            if match_name in match_names:
                raise serializers.ValidationError("이미 league와 title이 동일한 데이터가 존재합니다.")
            match_names.append(match_name)

        return matches


class MatchSerializer(serializers.ModelSerializer):
    league = serializers.SlugRelatedField(
        queryset=League.objects.all(), slug_field="name"
    )
    map = CreatableSlugRelatedField(queryset=Map.objects.all(), slug_field="name")
    player_tuples = PlayerTupleSerializer(
        many=True, required=True, allow_empty=False, min_length=1
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
            "player_tuples",
        ]
        extra_kwargs = {
            "date": {"required": True},
            "title": {"required": True},
            "miscellaneous": {"required": False, "allow_blank": True},
        }
        validators = [
            UniqueTogetherValidator(
                queryset=Match.objects.all(),
                fields=["league", "title"],
                message="이미 league와 title이 동일한 데이터가 존재합니다.",
            ),
        ]
        list_serializer_class = MatchListSerializer

    def create(self, validated_data):
        self.get_data_from_validated_data(validated_data=validated_data)

        with transaction.atomic():
            self.create_match()
            self.create_player_tuples()

            self.league = self.match.league
            if self.is_melee_match() and self.is_league_elo_rating_active():
                create_elo(player_tuple=self.player_tuples_instance[0])
        return self.match

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
        self.player_tuples_instance = player_serializer.create(
            validated_data=self.player_tuples, match=self.match
        )

    def update(self, instance, validated_data):
        player_tuples_validated_data = validated_data.pop("player_tuples")
        player_tuples_instance = instance.get_related_player_tuples()
        self.player_serializer = PlayerTupleSerializer(many=True)

        with transaction.atomic():
            self.player_tuples_instance = self.player_serializer.update(
                instance=player_tuples_instance,
                validated_data=player_tuples_validated_data,
            )
            instance = super().update(instance=instance, validated_data=validated_data)

            self.league = instance.league
            if (
                self.is_melee_match()
                and self.is_league_elo_rating_active()
                and self.player_tuples_changed()
            ):
                update_all_elo_related_with_league(league=self.league)
            return instance

    def is_melee_match(self):
        return len(self.player_tuples_instance) == 1

    def is_league_elo_rating_active(self):
        return self.league.is_elo_rating_active

    def player_tuples_changed(self):
        return self.player_serializer.has_changed


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


class MapStatisticsSerializer(WinRatioByRaceSerializer):
    total_matches_count = serializers.IntegerField()
