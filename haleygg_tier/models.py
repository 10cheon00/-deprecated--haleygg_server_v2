from django.db import models

from haleygg.models import League
from haleygg.models import Player


class PlayerTier(models.Model):
    TIER_LIST = [
        ("1티어", "1티어"),
        ("2티어", "2티어"),
        ("3티어", "3티어"),
        ("4티어", "4티어"),
        ("메이저", "메이저"),
        ("마이너", "마이너"),
        ("루키", "루키"),
    ]
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    tier = models.CharField(default="", choices=TIER_LIST, max_length=20)

    class Meta:
        ordering = ("league", "player", "tier")
        constraints = [
            models.UniqueConstraint(fields=["league", "player"], name="unique tier")
        ]

    def __str__(self):
        return f"{self.league} - {self.player}"
