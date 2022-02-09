from django.db import models
from django.db.models import Count
from django.db.models import Q
from django.db.models import Sum
from django.db.models.functions import Coalesce


class MatchStatisticsQueryset(models.QuerySet):
    def get_win_ratio_by_race(self):
        return self.aggregate(
            protoss_wins_to_terran_count=Count(
                "id",
                filter=Q(players__win_state=True)
                & Q(players__race="P")
                & Q(players__opponent__race="T"),
            ),
            protoss_wins_to_zerg_count=Count(
                "id",
                filter=Q(players__win_state=True)
                & Q(players__race="P")
                & Q(players__opponent__race="Z"),
            ),
            terran_wins_to_protoss_count=Count(
                "id",
                filter=Q(players__win_state=True)
                & Q(players__race="T")
                & Q(players__opponent__race="P"),
            ),
            terran_wins_to_zerg_count=Count(
                "id",
                filter=Q(players__win_state=True)
                & Q(players__race="T")
                & Q(players__opponent__race="Z"),
            ),
            zerg_wins_to_protoss_count=Count(
                "id",
                filter=Q(players__win_state=True)
                & Q(players__race="Z")
                & Q(players__opponent__race="P"),
            ),
            zerg_wins_to_terran_count=Count(
                "id",
                filter=Q(players__win_state=True)
                & Q(players__race="Z")
                & Q(players__opponent__race="T"),
            ),
            protoss_loses_to_terran_count=Count(
                "id",
                filter=Q(players__win_state=False)
                & Q(players__race="P")
                & Q(players__opponent__race="T"),
            ),
            protoss_loses_to_zerg_count=Count(
                "id",
                filter=Q(players__win_state=False)
                & Q(players__race="P")
                & Q(players__opponent__race="Z"),
            ),
            terran_loses_to_protoss_count=Count(
                "id",
                filter=Q(players__win_state=False)
                & Q(players__race="T")
                & Q(players__opponent__race="P"),
            ),
            terran_loses_to_zerg_count=Count(
                "id",
                filter=Q(players__win_state=False)
                & Q(players__race="T")
                & Q(players__opponent__race="Z"),
            ),
            zerg_loses_to_protoss_count=Count(
                "id",
                filter=Q(players__win_state=False)
                & Q(players__race="Z")
                & Q(players__opponent__race="P"),
            ),
            zerg_loses_to_terran_count=Count(
                "id",
                filter=Q(players__win_state=False)
                & Q(players__race="Z")
                & Q(players__opponent__race="T"),
            ),
        )

    def get_player_statistics(self, profile):
        return self.annotate(
            melee_winning=Count(
                "id",
                filter=Q(players__profile=profile)
                & Q(is_melee_match=True)
                & Q(players__win_state=True),
            ),
            melee_losing=Count(
                "id",
                filter=Q(players__profile=profile)
                & Q(is_melee_match=True)
                & Q(players__win_state=False),
            ),
            top_and_bottom_winning=Count(
                "id",
                filter=Q(players__profile=profile)
                & Q(is_melee_match=False)
                & Q(players__win_state=True),
            ),
            top_and_bottom_losing=Count(
                "id",
                filter=Q(players__profile=profile)
                & Q(is_melee_match=False)
                & Q(players__win_state=False),
            ),
        ).aggregate(
            protoss_wins_to_terran_count=Count(
                "id",
                filter=Q(players__profile=profile)
                & Q(players__win_state=True)
                & Q(players__race="P")
                & Q(players__opponent__race="T"),
            ),
            protoss_wins_to_zerg_count=Count(
                "id",
                filter=Q(players__profile=profile)
                & Q(players__win_state=True)
                & Q(players__race="P")
                & Q(players__opponent__race="Z"),
            ),
            terran_wins_to_protoss_count=Count(
                "id",
                filter=Q(players__profile=profile)
                & Q(players__win_state=True)
                & Q(players__race="T")
                & Q(players__opponent__race="P"),
            ),
            terran_wins_to_zerg_count=Count(
                "id",
                filter=Q(players__profile=profile)
                & Q(players__win_state=True)
                & Q(players__race="T")
                & Q(players__opponent__race="Z"),
            ),
            zerg_wins_to_protoss_count=Count(
                "id",
                filter=Q(players__profile=profile)
                & Q(players__win_state=True)
                & Q(players__race="Z")
                & Q(players__opponent__race="P"),
            ),
            zerg_wins_to_terran_count=Count(
                "id",
                filter=Q(players__profile=profile)
                & Q(players__win_state=True)
                & Q(players__race="Z")
                & Q(players__opponent__race="T"),
            ),
            protoss_loses_to_terran_count=Count(
                "id",
                filter=Q(players__profile=profile)
                & Q(players__win_state=False)
                & Q(players__race="P")
                & Q(players__opponent__race="T"),
            ),
            protoss_loses_to_zerg_count=Count(
                "id",
                filter=Q(players__profile=profile)
                & Q(players__win_state=False)
                & Q(players__race="P")
                & Q(players__opponent__race="Z"),
            ),
            terran_loses_to_protoss_count=Count(
                "id",
                filter=Q(players__profile=profile)
                & Q(players__win_state=False)
                & Q(players__race="T")
                & Q(players__opponent__race="P"),
            ),
            terran_loses_to_zerg_count=Count(
                "id",
                filter=Q(players__profile=profile)
                & Q(players__win_state=False)
                & Q(players__race="T")
                & Q(players__opponent__race="Z"),
            ),
            zerg_loses_to_protoss_count=Count(
                "id",
                filter=Q(players__profile=profile)
                & Q(players__win_state=False)
                & Q(players__race="Z")
                & Q(players__opponent__race="P"),
            ),
            zerg_loses_to_terran_count=Count(
                "id",
                filter=Q(players__profile=profile)
                & Q(players__win_state=False)
                & Q(players__race="Z")
                & Q(players__opponent__race="T"),
            ),
            melee_winning_count=Coalesce(Sum("melee_winning"), 0),
            melee_losing_count=Coalesce(Sum("melee_losing"), 0),
            top_and_bottom_winning_count=Coalesce(Sum("top_and_bottom_winning"), 0),
            top_and_bottom_losing_count=Coalesce(Sum("top_and_bottom_losing"), 0),
        )
