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


def get_elo_history_of_player(league_type, player_name):
    return (
        Elo.objects.filter(player_tuple__match__league__type=league_type)
        .filter(
            Q(player_tuple__winner__name__iexact=player_name)
            | Q(player_tuple__loser__name__iexact=player_name)
        )
        .annotate(
            rating=Case(
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
        .values("rating", "date")
    )


def get_elo_ranking(league_type):
    player_elo_queryset = (
        Elo.objects.select_related(
            "player_tuple", "player_tuple__match", "player_tuple__match__league"
        )
        .filter(player_tuple__match__league__type=league_type)
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


def create_total_elo_data(league_type):
    player_tuples_queryset = PlayerTuple.objects.select_related(
        "match", "winner", "loser", "match__league"
    ).filter(match__league__type=league_type)

    duplicated_matches_count = (
        player_tuples_queryset.filter(match=OuterRef("match"))
        .values("match")
        .annotate(match_count=Count("match"))
        .values("match_count")[:1]
    )

    melee_player_tuples = player_tuples_queryset.annotate(
        duplicated_matches_count=Subquery(duplicated_matches_count)
    ).exclude(duplicated_matches_count__gt=1)

    ratings = list()
    previous_rating_data = dict()

    for row in melee_player_tuples.iterator():
        import math

        # Get previous player rating
        winner = row.winner
        previous_winner_rating = (
            previous_rating_data[winner]
            if winner in previous_rating_data.keys()
            else Decimal(1000.0)
        )
        loser = row.loser
        previous_loser_rating = (
            previous_rating_data[loser]
            if loser in previous_rating_data.keys()
            else Decimal(1000.0)
        )

        # Calculate
        expected_winner_winning_rate = Decimal(
            1
            / (math.pow(10, (previous_loser_rating - previous_winner_rating) / 400) + 1)
        )

        winner_rating = K_FACTOR * (1 - expected_winner_winning_rate)
        loser_rating = -1 * winner_rating
        calculated_winner_rating = previous_winner_rating + winner_rating
        calculated_loser_rating = previous_loser_rating + loser_rating

        # Save and memorize
        previous_rating_data[winner] = calculated_winner_rating
        previous_rating_data[loser] = calculated_loser_rating
        ratings.append(
            Elo(
                player_tuple_id=row.id,
                winner_rating=calculated_winner_rating,
                loser_rating=calculated_loser_rating,
            )
        )

    print(len(Elo.objects.bulk_create(ratings)))
