from decimal import Decimal

from django.db import models
from django.db.models import F
from django.db.models import Q
from django.db.models import Case
from django.db.models import When

from haleygg.models import Match
from haleygg.models import PlayerTuple


class Elo(models.Model):
    player_tuple = models.OneToOneField(PlayerTuple, on_delete=models.CASCADE)
    winner_rating = models.DecimalField(default=1000.0, max_digits=6, decimal_places=1)
    loser_rating = models.DecimalField(default=1000.0, max_digits=6, decimal_places=1)

    objects = models.Manager()

    class Meta:
        ordering = ("player_tuple",)

    def __str__(self):
        return f"{self.player_tuple_id} Winner : {self.winner_rating} Loser : {self.loser_rating}"


def create_elo(player_tuple):
    previous_elo_queryset = Elo.objects.filter(
        Q(player_tuple__match__league=player_tuple.match.league)
        & (
            Q(player_tuple__match__date__lt=player_tuple.match.date)
            | (
                Q(player_tuple__match__date=player_tuple.match.date)
                & Q(player_tuple__match__title__lt=player_tuple.match.title)
            )
        )
    )

    previous_elo_of_winner = previous_elo_queryset.filter(
        Q(player_tuple__winner=player_tuple.winner)
        | Q(player_tuple__loser=player_tuple.winner)
    ).annotate(
        previous_elo=Case(
            When(
                condition=Q(player_tuple__winner=player_tuple.winner),
                then=F("winner_rating"),
            ),
            When(
                condition=Q(player_tuple__loser=player_tuple.winner),
                then=F("loser_rating"),
            ),
        )
    )

    previous_elo_of_loser = previous_elo_queryset.filter(
        Q(player_tuple__winner=player_tuple.loser)
        | Q(player_tuple__loser=player_tuple.loser)
    ).annotate(
        previous_elo=Case(
            When(
                condition=Q(player_tuple__winner=player_tuple.loser),
                then=F("winner_rating"),
            ),
            When(
                condition=Q(player_tuple__loser=player_tuple.loser),
                then=F("loser_rating"),
            ),
        )
    )

    if previous_elo_of_winner.exists():
        previous_elo_of_winner = previous_elo_of_winner.last().previous_elo
    else:
        previous_elo_of_winner = Decimal(1000.0)

    if previous_elo_of_loser.exists():
        previous_elo_of_loser = previous_elo_of_loser.last().previous_elo
    else:
        previous_elo_of_loser = Decimal(1000.0)

    calculated_elo_of_winner, calculated_elo_of_loser = calculate_elo(
        previous_elo_of_winner=previous_elo_of_winner,
        previous_elo_of_loser=previous_elo_of_loser,
        k=player_tuple.match.league.k_factor,
    )

    Elo.objects.create(
        player_tuple=player_tuple,
        winner_rating=calculated_elo_of_winner,
        loser_rating=calculated_elo_of_loser,
    )

    if (
        Match.objects.filter(league=player_tuple.match.league).last()
        != player_tuple.match
    ):
        update_all_elo_related_with_league(league=player_tuple.match.league)


def update_all_elo_related_with_league(league):
    queryset = Elo.objects.filter(player_tuple__match__league=league)

    previous_elo_data = dict()

    for row in queryset:
        previous_elo_of_winner = previous_elo_data.get(
            row.player_tuple.winner, Decimal(1000.0)
        )
        previous_elo_of_loser = previous_elo_data.get(
            row.player_tuple.loser, Decimal(1000.0)
        )
        calculated_elo_of_winner, calculated_elo_of_loser = calculate_elo(
            previous_elo_of_winner=previous_elo_of_winner,
            previous_elo_of_loser=previous_elo_of_loser,
            k=row.player_tuple.match.league.k_factor,
        )
        row.winner_rating = calculated_elo_of_winner
        row.loser_rating = calculated_elo_of_loser
        previous_elo_data[row.player_tuple.winner] = calculated_elo_of_winner
        previous_elo_data[row.player_tuple.loser] = calculated_elo_of_loser

    Elo.objects.bulk_update(queryset, ["winner_rating", "loser_rating"])


def calculate_elo(previous_elo_of_winner, previous_elo_of_loser, k):
    import math

    winner_expected_winning_percentage = Decimal(
        1 / (math.pow(10, (previous_elo_of_loser - previous_elo_of_winner) / 400) + 1)
    )
    calculated_elo_of_winner = k * (1 - winner_expected_winning_percentage)
    calculated_elo_of_loser = -1 * calculated_elo_of_winner
    return (
        previous_elo_of_winner + calculated_elo_of_winner,
        previous_elo_of_loser + calculated_elo_of_loser,
    )
