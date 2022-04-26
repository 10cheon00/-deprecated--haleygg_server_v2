from decimal import Decimal

from django.db import models
from django.db.models import Case
from django.db.models import Count
from django.db.models import F
from django.db.models import Q
from django.db.models import OuterRef
from django.db.models import Subquery
from django.db.models import When

from haleygg.models import Player
from haleygg.models import PlayerTuple


K_FACTOR = 32


class Elo(models.Model):
    player_tuple = models.OneToOneField(PlayerTuple, on_delete=models.CASCADE)
    winner_rating = models.DecimalField(
        default=1000.0, max_digits=6, decimal_places=1, verbose_name="승자 Elo"
    )
    loser_rating = models.DecimalField(
        default=1000.0, max_digits=6, decimal_places=1, verbose_name="패자 Elo"
    )

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


def get_elo_history_of_player(league_name, player_name):
    return (
        Elo.objects.filter(player_tuple__match__league__name__iexact=league_name)
        .filter(
            Q(player_tuple__winner__name__iexact=player_name)
            | Q(player_tuple__loser__name__iexact=player_name)
        )
        .annotate(
            elo=Case(
                When(
                    condition=Q(player_tuple__winner__name__iexact=player_name),
                    then=F("winner_rating"),
                ),
                When(
                    condition=Q(player_tuple__loser__name__iexact=player_name),
                    then=F("loser_rating"),
                ),
                default=Decimal(1000.0),
            ),
            date=F("player_tuple__match__date"),
        )
        .values("elo", "date")
    )


def get_elo_ranking(league_name):
    player_elo_queryset = (
        Elo.objects.filter(player_tuple__match__league__name__iexact=league_name)
        .filter(
            Q(player_tuple__winner=OuterRef("id"))
            | Q(player_tuple__loser=OuterRef("id"))
        )
        .annotate(
            elo=Case(
                When(
                    condition=Q(player_tuple__winner=OuterRef("id")),
                    then=F("winner_rating"),
                ),
                When(
                    condition=Q(player_tuple__loser=OuterRef("id")),
                    then=F("loser_rating"),
                ),
                default=Decimal(1000.0),
            ),
        )
    )
    ranking_queryset = (
        Player.objects.annotate(
            current_elo=Subquery(player_elo_queryset.reverse().values("elo")[:1]),
        )
        .filter(current_elo__isnull=False)
        .values("name", "current_elo", "favorate_race")
        .order_by("-current_elo")
    )
    return ranking_queryset
