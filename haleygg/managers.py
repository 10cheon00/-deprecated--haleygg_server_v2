from django.db import models
from django.db.models import Count
from django.db.models import Q


class MatchStatisticsQueryset(models.QuerySet):
    def get_map_statistics(self, map):
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

    def get_player_statistics(self, player):
        statistics = {}
        statistics.update(self.get_player_melee_statistics(player))
        statistics.update(self.get_player_top_and_bottom_statistics(player))
        return statistics

    def get_player_melee_statistics(self, player):
        return (
            self.get_melee_matches()
            .filter(Q(player_tuples__winner=player) | Q(player_tuples__loser=player))
            .aggregate(
                winning_melee_matches_count=Count(
                    "id", filter=Q(player_tuples__winner=player)
                ),
                losing_melee_matches_count=Count(
                    "id", filter=Q(player_tuples__loser=player)
                ),
                protoss_wins_to_terran_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="P")
                    & Q(player_tuples__loser_race="T")
                    & Q(player_tuples__winner=player),
                ),
                protoss_wins_to_zerg_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="P")
                    & Q(player_tuples__loser_race="Z")
                    & Q(player_tuples__winner=player),
                ),
                terran_wins_to_protoss_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="T")
                    & Q(player_tuples__loser_race="P")
                    & Q(player_tuples__winner=player),
                ),
                terran_wins_to_zerg_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="T")
                    & Q(player_tuples__loser_race="Z")
                    & Q(player_tuples__winner=player),
                ),
                zerg_wins_to_terran_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="Z")
                    & Q(player_tuples__loser_race="T")
                    & Q(player_tuples__winner=player),
                ),
                zerg_wins_to_protoss_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="Z")
                    & Q(player_tuples__loser_race="P")
                    & Q(player_tuples__winner=player),
                ),
                protoss_loses_to_terran_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="P")
                    & Q(player_tuples__loser_race="T")
                    & Q(player_tuples__loser=player),
                ),
                protoss_loses_to_zerg_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="P")
                    & Q(player_tuples__loser_race="Z")
                    & Q(player_tuples__loser=player),
                ),
                terran_loses_to_protoss_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="T")
                    & Q(player_tuples__loser_race="P")
                    & Q(player_tuples__loser=player),
                ),
                terran_loses_to_zerg_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="T")
                    & Q(player_tuples__loser_race="Z")
                    & Q(player_tuples__loser=player),
                ),
                zerg_loses_to_terran_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="Z")
                    & Q(player_tuples__loser_race="T")
                    & Q(player_tuples__loser=player),
                ),
                zerg_loses_to_protoss_count=Count(
                    "id",
                    filter=Q(player_tuples__winner_race="Z")
                    & Q(player_tuples__loser_race="P")
                    & Q(player_tuples__loser=player),
                ),
            )
        )

    def get_melee_matches(self):
        return self.annotate(player_tuples_count=Count("player_tuples")).filter(
            player_tuples_count=1
        )

    def get_player_top_and_bottom_statistics(self, player):
        return (
            self.get_top_and_bottom_matches()
            .filter(Q(player_tuples__winner=player) | Q(player_tuples__loser=player))
            .aggregate(
                winning_top_and_bottom_matches_count=Count(
                    "id", filter=Q(player_tuples__winner=player)
                ),
                losing_top_and_bottom_matches_count=Count(
                    "id", filter=Q(player_tuples__loser=player)
                ),
            )
        )

    def get_top_and_bottom_matches(self):
        return self.annotate(player_tuples_count=Count("player_tuples")).filter(
            player_tuples_count__gt=1
        )
