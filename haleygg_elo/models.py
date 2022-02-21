from django.db import models

from haleygg.models import Profile
from haleygg.models import Match


class Elo(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    rating = models.DecimalField(default=1000.0, max_digits=7, decimal_places=2)

    class Meta:
        ordering = ("match",)

    def __str__(self):
        return f"{self.profile} - {self.rating}"


def create_elo(player_tuple):
    from decimal import Decimal

    latest_elo_rating_of_winner = Decimal(1000.00)
    latest_row_of_winner = Elo.objects.filter(
        profile=player_tuple.winner, match__league=player_tuple.match.league
    ).last()
    if latest_row_of_winner is not None:
        latest_elo_rating_of_winner = latest_row_of_winner.rating

    latest_elo_rating_of_loser = Decimal(1000.00)
    latest_row_of_loser = Elo.objects.filter(
        profile=player_tuple.loser, match__league=player_tuple.match.league
    ).last()
    if latest_row_of_loser is not None:
        latest_elo_rating_of_loser = latest_row_of_loser.rating

    k = player_tuple.match.league.k_factor

    winner_rating, loser_rating = calculate_elo(
        latest_elo_rating_of_winner=latest_elo_rating_of_winner,
        latest_elo_rating_of_loser=latest_elo_rating_of_loser,
        k=k,
    )

    Elo.objects.create(
        profile=player_tuple.winner,
        match=player_tuple.match,
        rating=latest_elo_rating_of_winner + Decimal(value=winner_rating),
    )
    Elo.objects.create(
        profile=player_tuple.loser,
        match=player_tuple.match,
        rating=latest_elo_rating_of_loser + Decimal(value=loser_rating),
    )


# TODO
# Update All record what created after match.
def update_elo(match):
    pass


def calculate_elo(latest_elo_rating_of_winner, latest_elo_rating_of_loser, k):
    import math

    winner_expected_winning_percentage = 1 / (
        math.pow(10, (latest_elo_rating_of_loser - latest_elo_rating_of_winner) / 400)
        + 1
    )
    winner_rating = k * (1 - winner_expected_winning_percentage)
    loser_rating = -1 * winner_rating
    return (winner_rating, loser_rating)
