from django.db import models
from django.utils import timezone

from haleygg.managers import MatchStatisticsQueryset


class League(models.Model):
    name = models.CharField(default="", max_length=30, unique=True)

    def __str__(self):
        return self.name


class Map(models.Model):
    name = models.CharField(default="", max_length=30, unique=True)
    image_url = models.URLField(max_length=200, null=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    RACE_LIST = [("P", "Protoss"), ("T", "Terran"), ("Z", "Zerg")]
    name = models.CharField(default="", max_length=30, unique=True)
    joined_date = models.DateField(default=timezone.now)
    favorate_race = models.CharField(choices=RACE_LIST, default="", max_length=10)
    career = models.TextField(default="", max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.name


class Match(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="matches")
    date = models.DateField(default=timezone.now)
    title = models.CharField(default="", max_length=100)
    map = models.ForeignKey(Map, on_delete=models.CASCADE, related_name="matches")
    miscellaneous = models.CharField(default="", max_length=100, blank=True)
    is_melee_match = models.BooleanField(default=True)

    objects = models.Manager()
    statistics = MatchStatisticsQueryset.as_manager()

    class Meta:
        ordering = ["-date", "-league", "-title"]
        unique_together = ("league", "title")

    def __str__(self):
        return f"Date: {self.date}, League: {self.league_id}, Title: {self.title}, Map: {self.map_id}"

    def get_related_players(self):
        return self.players.all()


class Player(models.Model):
    RACE_LIST = [("P", "Protoss"), ("T", "Terran"), ("Z", "Zerg")]
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="players")
    opponent = models.ForeignKey(
        "self", blank=True, on_delete=models.SET_NULL, null=True
    )
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    race = models.CharField(choices=RACE_LIST, default="", max_length=10)
    win_state = models.BooleanField(default=False)

    def __str__(self):
        win_state_str = "승"
        if not self.win_state:
            win_state_str = "패"

        return f"Match: {self.match_id}, Profile: {self.profile_id}, Race: {self.race}, isWin: {win_state_str}"
