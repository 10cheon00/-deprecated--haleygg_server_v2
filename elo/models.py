from django.db import models

from haleygg.models import League
from haleygg.models import Profile


class AbstractElo(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    value = models.IntegerField(default=1000)

    class Meta:
        abstract = True


class Elo(AbstractElo):
    def save(self, *args, **kwargs):
        elo = super().save(*args, **kwargs)

        EloHistory.objects.create(
            elo=elo, profile=elo.profile, league=elo.league, value=elo.value
        )


class EloHistory(AbstractElo):
    elo = models.ForeignKey(Elo, on_delete=models.CASCADE, related_name="elo_histories")
