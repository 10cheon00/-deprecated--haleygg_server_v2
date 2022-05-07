from django.db import models
from django.db.models import Count
from django.db.models import F
from django.db.models import Q
from django.db.models import OuterRef
from django.db.models import Subquery
from django.db.models.functions import Coalesce


class MatchStatisticsQueryset(models.QuerySet):
    def get_map_statistics(self):
        return self.get_melee_matches().aggregate(
            total_matches_count=Count("id"),
            protoss_wins_to_terran_count=Count(
                "id",
                filter=Q(player_tuples__winner_race="P")
                & Q(player_tuples__loser_race="T"),
            ),
            protoss_wins_to_zerg_count=Count(
                "id",
                filter=Q(player_tuples__winner_race="P")
                & Q(player_tuples__loser_race="Z"),
            ),
            terran_wins_to_protoss_count=Count(
                "id",
                filter=Q(player_tuples__winner_race="T")
                & Q(player_tuples__loser_race="P"),
            ),
            terran_wins_to_zerg_count=Count(
                "id",
                filter=Q(player_tuples__winner_race="T")
                & Q(player_tuples__loser_race="Z"),
            ),
            zerg_wins_to_protoss_count=Count(
                "id",
                filter=Q(player_tuples__winner_race="Z")
                & Q(player_tuples__loser_race="P"),
            ),
            zerg_wins_to_terran_count=Count(
                "id",
                filter=Q(player_tuples__winner_race="Z")
                & Q(player_tuples__loser_race="T"),
            ),
        )

    def get_win_ratio_by_race(self):
        return self.get_melee_matches().aggregate(
            protoss_wins_to_terran_count=Count(
                "id",
                filter=Q(player_tuples__winner_race="P")
                & Q(player_tuples__loser_race="T"),
            ),
            protoss_wins_to_zerg_count=Count(
                "id",
                filter=Q(player_tuples__winner_race="P")
                & Q(player_tuples__loser_race="Z"),
            ),
            terran_wins_to_protoss_count=Count(
                "id",
                filter=Q(player_tuples__winner_race="T")
                & Q(player_tuples__loser_race="P"),
            ),
            terran_wins_to_zerg_count=Count(
                "id",
                filter=Q(player_tuples__winner_race="T")
                & Q(player_tuples__loser_race="Z"),
            ),
            zerg_wins_to_protoss_count=Count(
                "id",
                filter=Q(player_tuples__winner_race="Z")
                & Q(player_tuples__loser_race="P"),
            ),
            zerg_wins_to_terran_count=Count(
                "id",
                filter=Q(player_tuples__winner_race="Z")
                & Q(player_tuples__loser_race="T"),
            ),
        )

    def get_player_statistics(self, player_name):
        statistics = {}
        statistics.update(self.get_player_melee_statistics(player_name))
        statistics.update(self.get_player_top_and_bottom_statistics(player_name))
        return statistics

    def get_player_melee_statistics(self, player_name):
        return (
            self.get_melee_matches()
            .filter(
                Q(player_tuples__winner__name__iexact=player_name)
                | Q(player_tuples__loser__name__iexact=player_name)
            )
            .aggregate(
                winning_melee_matches_count=Count(
                    "id", filter=Q(player_tuples__winner__name__iexact=player_name)
                ),
                losing_melee_matches_count=Count(
                    "id", filter=Q(player_tuples__loser__name__iexact=player_name)
                ),
                protoss_wins_to_protoss_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="P")
                    & Q(player_tuples__loser_race="P")
                    & Q(player_tuples__winner__name__iexact=player_name),
                ),
                protoss_wins_to_terran_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="P")
                    & Q(player_tuples__loser_race="T")
                    & Q(player_tuples__winner__name__iexact=player_name),
                ),
                protoss_wins_to_zerg_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="P")
                    & Q(player_tuples__loser_race="Z")
                    & Q(player_tuples__winner__name__iexact=player_name),
                ),
                terran_wins_to_protoss_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="T")
                    & Q(player_tuples__loser_race="P")
                    & Q(player_tuples__winner__name__iexact=player_name),
                ),
                terran_wins_to_terran_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="T")
                    & Q(player_tuples__loser_race="T")
                    & Q(player_tuples__winner__name__iexact=player_name),
                ),
                terran_wins_to_zerg_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="T")
                    & Q(player_tuples__loser_race="Z")
                    & Q(player_tuples__winner__name__iexact=player_name),
                ),
                zerg_wins_to_protoss_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="Z")
                    & Q(player_tuples__loser_race="P")
                    & Q(player_tuples__winner__name__iexact=player_name),
                ),
                zerg_wins_to_terran_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="Z")
                    & Q(player_tuples__loser_race="T")
                    & Q(player_tuples__winner__name__iexact=player_name),
                ),
                zerg_wins_to_zerg_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="Z")
                    & Q(player_tuples__loser_race="Z")
                    & Q(player_tuples__winner__name__iexact=player_name),
                ),
                protoss_loses_to_protoss_count=Count(
                    "id",
                    filter=Q(player_tuples__loser_race="P")
                    & Q(player_tuples__winner_race="P")
                    & Q(player_tuples__loser__name__iexact=player_name),
                ),
                protoss_loses_to_terran_count=Count(
                    "id",
                    filter=Q(player_tuples__loser_race="P")
                    & Q(player_tuples__winner_race="T")
                    & Q(player_tuples__loser__name__iexact=player_name),
                ),
                protoss_loses_to_zerg_count=Count(
                    "id",
                    filter=Q(player_tuples__loser_race="P")
                    & Q(player_tuples__winner_race="Z")
                    & Q(player_tuples__loser__name__iexact=player_name),
                ),
                terran_loses_to_protoss_count=Count(
                    "id",
                    filter=Q(player_tuples__loser_race="T")
                    & Q(player_tuples__winner_race="P")
                    & Q(player_tuples__loser__name__iexact=player_name),
                ),
                terran_loses_to_terran_count=Count(
                    "id",
                    filter=Q(player_tuples__loser_race="T")
                    & Q(player_tuples__winner_race="T")
                    & Q(player_tuples__loser__name__iexact=player_name),
                ),
                terran_loses_to_zerg_count=Count(
                    "id",
                    filter=Q(player_tuples__loser_race="T")
                    & Q(player_tuples__winner_race="Z")
                    & Q(player_tuples__loser__name__iexact=player_name),
                ),
                zerg_loses_to_protoss_count=Count(
                    "id",
                    filter=Q(player_tuples__loser_race="Z")
                    & Q(player_tuples__winner_race="P")
                    & Q(player_tuples__loser__name__iexact=player_name),
                ),
                zerg_loses_to_terran_count=Count(
                    "id",
                    filter=Q(player_tuples__loser_race="Z")
                    & Q(player_tuples__winner_race="T")
                    & Q(player_tuples__loser__name__iexact=player_name),
                ),
                zerg_loses_to_zerg_count=Count(
                    "id",
                    filter=Q(player_tuples__loser_race="Z")
                    & Q(player_tuples__winner_race="Z")
                    & Q(player_tuples__loser__name__iexact=player_name),
                ),
            )
        )

    def get_melee_matches(self):
        return self.annotate(player_tuples_count=Count("player_tuples")).filter(
            player_tuples_count=1
        )

    def get_player_top_and_bottom_statistics(self, player_name):
        return (
            self.get_top_and_bottom_matches()
            .filter(
                Q(player_tuples__winner__name__iexact=player_name)
                | Q(player_tuples__loser__name__iexact=player_name)
            )
            .aggregate(
                winning_top_and_bottom_matches_count=Count(
                    "id", filter=Q(player_tuples__winner__name__iexact=player_name)
                ),
                losing_top_and_bottom_matches_count=Count(
                    "id", filter=Q(player_tuples__loser__name__iexact=player_name)
                ),
            )
        )

    def get_top_and_bottom_matches(self):
        return self.annotate(player_tuples_count=Count("player_tuples")).filter(
            player_tuples_count__gt=1
        )


class PlayerRankManager(models.Manager):
    def board(self, query_params):
        self.query_params = query_params

        self.create_match_type_filter()
        self.create_field_filter()

        return self.get_queryset_with_category()

    def create_match_type_filter(self):
        # Create subquery by match type (melee, top and bottom)
        from haleygg.models import PlayerTuple

        self.player_matches = PlayerTuple.objects
        match_type = self.query_params.get("match_type")

        if match_type == "melee":
            self.player_matches = self.player_matches.annotate(
                related_matches_count=Subquery(
                    PlayerTuple.objects.filter(match=OuterRef("match"))
                    .values("match")
                    .annotate(count=Count("id"))
                    .values("count")
                )
            ).filter(
                related_matches_count=1,
            )
        elif match_type == "top_and_bottom":
            self.player_matches = self.player_matches.annotate(
                related_matches_count=Subquery(
                    PlayerTuple.objects.filter(match=OuterRef("match"))
                    .values("match")
                    .annotate(count=Count("id"))
                    .values("count")
                )
            ).filter(
                related_matches_count__gt=1,
            )

    def create_field_filter(self):
        # Create Q objects by field query parameters.
        # (League, League's type, Map)
        self.field_filters = Q()

        league_name = self.query_params.get("league")
        league_type = self.query_params.get("league__type")
        map_name = self.query_params.get("map")

        if league_name:
            self.field_filters &= Q(match__league__name=league_name)

        if league_type:
            self.field_filters &= Q(match__league__type=league_type)

        if map_name:
            self.field_filters &= Q(match__map__name=map_name)

    def get_queryset_with_category(self):
        # Return queryset by category.(Total, Win, Lose)
        queryset = super().get_queryset()

        category = self.query_params.get("category")

        if category is None:
            category = "total"

        if category == "win" or category == "total":
            queryset = queryset.annotate(
                winner_count=Coalesce(
                    Subquery(
                        self.player_matches.filter(
                            Q(winner=OuterRef("id")) & self.field_filters
                        )
                        .values("winner")
                        .annotate(count=Count("winner"))
                        .values("count")
                    ),
                    0,
                )
            )
            result_field = "winner_count"

        if category == "lose" or category == "total":
            queryset = queryset.annotate(
                loser_count=Coalesce(
                    Subquery(
                        self.player_matches.filter(
                            Q(loser=OuterRef("id")) & self.field_filters
                        )
                        .values("loser")
                        .annotate(count=Count("loser"))
                        .values("count")
                    ),
                    0,
                ),
            )
            result_field = "loser_count"

        if category == "total":
            queryset = queryset.annotate(
                total_count=F("winner_count") + F("loser_count")
            )
            result_field = "total_count"

        queryset = (
            queryset.annotate(value=F(result_field))
            .order_by("-value", "name")
            .filter(value__gt=0)
        )

        return queryset
