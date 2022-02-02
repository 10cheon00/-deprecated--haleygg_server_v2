from django.db import models
from django.utils import timezone


class League(models.Model):
    name = models.CharField(default="", max_length=30)


class Map(models.Model):
    image_url = models.URLField(max_length=200, null=True)
    name = models.CharField(default="", max_length=30)


class Profile(models.Model):
    RACE_LIST = [("P", "Protoss"), ("T", "Terran"), ("Z", "Zerg")]
    career = models.TextField(default="", max_length=1000)
    favorate_race = models.CharField(choices=RACE_LIST, default="P", max_length=30)
    name = models.CharField(default="", max_length=30)
    joined_date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name


class Match(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="matches")
    date = models.DateField(default=timezone.now)
    title = models.CharField(default="", max_length=100)
    map = models.ForeignKey(Map, on_delete=models.CASCADE, related_name="matches")
    miscellaneous = models.CharField(default="", max_length=100)
    is_melee_match = models.BooleanField(default=True)

    def __str__(self):
        return (
            f"{self.date} - {self.league.__str__()} {self.title} - {self.map.__str__()}"
        )


class Player(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="players")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    win_state = models.BooleanField(default=False)
