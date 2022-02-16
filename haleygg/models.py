from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from haleygg.managers import MatchStatisticsQueryset


class League(models.Model):
    name = models.CharField(default="", max_length=30, unique=True, verbose_name="이름")

    def __str__(self):
        return self.name


def validate_image(image):
    from django.core.exceptions import ValidationError

    if image.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        raise ValidationError("The maximum file size that can be uploaded is 1MB.")
    return image


class Map(models.Model):
    name = models.CharField(default="", max_length=30, unique=True, verbose_name="이름")
    image = models.ImageField(
        upload_to="images/", validators=[validate_image], verbose_name="맵 이미지"
    )

    def __str__(self):
        return self.name


class Profile(models.Model):
    RACE_LIST = [("P", "Protoss"), ("T", "Terran"), ("Z", "Zerg")]
    name = models.CharField(default="", max_length=30, unique=True, verbose_name="이름")
    joined_date = models.DateField(default=timezone.now, verbose_name="가입한 날짜")
    favorate_race = models.CharField(
        choices=RACE_LIST, default="", max_length=10, verbose_name="선호 종족"
    )
    career = models.TextField(
        default="", max_length=1000, null=True, blank=True, verbose_name="커리어"
    )

    def __str__(self):
        return self.name


class Match(models.Model):
    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name="matches", verbose_name="리그"
    )
    date = models.DateField(default=timezone.now, verbose_name="날짜")
    title = models.CharField(default="", max_length=100, verbose_name="제목")
    map = models.ForeignKey(
        Map, on_delete=models.CASCADE, related_name="matches", verbose_name="맵"
    )
    miscellaneous = models.CharField(
        default="", max_length=100, blank=True, verbose_name="비고"
    )
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


@receiver(pre_save, sender=Match)
def set_is_melee_match(sender, instance, *args, **kwargs):
    players = instance.get_related_players().count()
    is_melee_match = True
    if players > 2:
        is_melee_match = False
    instance.is_melee_match = is_melee_match


class Player(models.Model):
    RACE_LIST = [("P", "Protoss"), ("T", "Terran"), ("Z", "Zerg")]
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="players")
    opponent = models.ForeignKey(
        "self", blank=True, on_delete=models.SET_NULL, null=True
    )
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name="플레이어")
    race = models.CharField(
        choices=RACE_LIST, default="", max_length=10, verbose_name="종족"
    )
    win_state = models.BooleanField(default=False, verbose_name="승리")

    def __str__(self):
        win_state_str = "승"
        if not self.win_state:
            win_state_str = "패"

        return f"Match: {self.match_id}, Profile: {self.profile_id}, Race: {self.race}, isWin: {win_state_str}"
