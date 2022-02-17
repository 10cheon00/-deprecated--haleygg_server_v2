from django.db import models

from haleygg.models import Player
from elo.managers import EloRankingQuerySet
from elo.managers import EloFilterQuerySet


class Elo(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE, primary_key=True)
    value = models.IntegerField(default=0)

    objects = models.Manager()
    ranking = EloRankingQuerySet.as_manager()
    filter = EloFilterQuerySet.as_manager()

    class Meta:
        ordering = ["-player__match__date"]

    def __str__(self):
        return f"{self.player} elo : {self.value}"
