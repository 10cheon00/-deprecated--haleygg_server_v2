from django.db import transaction
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework import exceptions

from server.models import League
from server.models import Match
from server.models import Map
from server.models import Player
from server.models import Profile


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


class PlayerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="profile.name")  # ☆

    class Meta:
        model = Player
        fields = ["id", "name", "win_state"]
        extra_kwargs = {"name": {"required": True}, "win_state": {"required": True}}


class MatchSerializer(serializers.ModelSerializer):
    league = serializers.CharField(source="league.name")
    map = serializers.CharField(source="map.name")
    players = PlayerSerializer(many=True, required=True, allow_empty=False)

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
            "players",  # ☆
        ]
        extra_kwargs = {
            "league": {"required": True},
            "date": {"required": True},
            "title": {"required": True},
            "map": {"required": True},
        }

    def create(self, validated_data):
        self.get_data_from_validated_data(validated_data)
        self.check_match_already_exists()
        with transaction.atomic():
            self.create_match()
            self.create_players()
        return self.match

    def get_data_from_validated_data(self, validated_data):
        try:
            self.league = League.objects.get(
                name=validated_data.get("league").get("name")
            )
            self.map = Map.objects.get(name=validated_data.get("map").get("name"))
            self.date = validated_data.get("date")
            self.title = validated_data.get("title")
            self.miscellaneous = validated_data.get("miscellaneous")
            self.is_melee_match = (
                True if len(validated_data.get("players")) > 2 else False
            )
            self.players = validated_data.pop("players")
            self.find_not_exists_players()

        except League.DoesNotExist:
            raise exceptions.NotFound(detail="존재하지 않는 리그입니다.")
        except Map.DoesNotExist:
            raise exceptions.NotFound(detail="존재하지 않는 맵입니다.")
        except Profile.DoesNotExist:
            raise exceptions.NotFound(detail="존재하지 않는 플레이어입니다.")

    def find_not_exists_players(self):
        self.player_names = [
            player.get("profile").get("name") for player in self.players
        ]
        profiles = Profile.objects.filter(name__in=self.player_names).values_list(
            "name", flat=True
        )
        duplicated_profile_names = list(set(self.player_names) - set(profiles))

        if duplicated_profile_names:
            raise Profile.DoesNotExist(duplicated_profile_names)

    def check_match_already_exists(self):
        if Match.objects.filter(
            league_id=self.league.id, title__iexact=self.title
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
        player_objects = []
        for player in self.players:
            player_name = player.get("profile").get("name")
            player_objects.append(
                Player(
                    match=self.match,
                    profile=Profile.objects.get(name=player_name),
                    win_state=player.get("win_state"),
                )
            )

        Player.objects.bulk_create(player_objects)
