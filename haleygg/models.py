from django.conf import settings
from django.db import models
from django.utils import timezone

from haleygg.managers import MatchStatisticsQueryset


def validate_image(image):
    from django.core.exceptions import ValidationError

    if image.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        raise ValidationError("The maximum file size that can be uploaded is 1MB.")
    return image


class Map(models.Model):
    name = models.CharField(default="", max_length=30, unique=True, verbose_name="이름")
    image = models.ImageField(
        upload_to="images/%Y/%m/%d",
        validators=[validate_image],
        verbose_name="맵 이미지",
        null=True,
    )
    type = models.CharField(
        choices=[("melee", "Melee"), ("top_and_bottom", "Top And Bottom")],
        default="melee",
        max_length=15,
    )

    class Meta:
        ordering = [
            "-name",
        ]

    def __str__(self):
        return self.name


class Player(models.Model):
    RACE_LIST = [("P", "Protoss"), ("T", "Terran"), ("Z", "Zerg")]
    name = models.CharField(default="", max_length=30, unique=True, verbose_name="이름")
    joined_date = models.DateField(default=timezone.now, verbose_name="가입한 날짜")
    favorate_race = models.CharField(
        choices=RACE_LIST, default="", max_length=1, verbose_name="선호 종족"
    )
    career = models.TextField(
        default="", max_length=1000, null=True, blank=True, verbose_name="커리어"
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class League(models.Model):
    TYPE_LIST = [
        ("starleague", "Starleague"),
        ("proleague", "Proleague"),
        ("other", "Other"),
    ]
    name = models.CharField(default="", max_length=30, unique=True)
    type = models.CharField(choices=TYPE_LIST, default="other", max_length=10)

    class Meta:
        ordering = (
            "type",
            "-name",
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
        default="", max_length=100, null=True, verbose_name="비고"
    )

    objects = models.Manager()
    statistics = MatchStatisticsQueryset.as_manager()

    class Meta:
        ordering = ("date", "league", "title")
        constraints = [
            models.UniqueConstraint(fields=["league", "title"], name="unique match")
        ]

    def __str__(self):
        return f"Date: {self.date}, League: {self.league_id}, Title: {self.title}, Map: {self.map_id}"

    def get_related_player_tuples(self):
        return self.player_tuples.all().select_related("winner", "loser")


class PlayerTuple(models.Model):
    RACE_LIST = [("P", "Protoss"), ("T", "Terran"), ("Z", "Zerg"), ("R", "Random")]
    match = models.ForeignKey(
        Match, on_delete=models.CASCADE, related_name="player_tuples"
    )
    winner = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="winners", verbose_name="승리자"
    )
    loser = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="losers", verbose_name="패배자"
    )
    winner_race = models.CharField(
        choices=RACE_LIST,
        default="",
        max_length=1,
        verbose_name="승리자 종족",
    )
    loser_race = models.CharField(
        choices=RACE_LIST,
        default="",
        max_length=1,
        verbose_name="패배자 종족",
    )

    class Meta:
        ordering = ("match",)

    def __str__(self):
        return f"Match: {self.match_id}"
        #  Winner: {self.winner} ({self.winner_race}) Loser: {self.loser} ({self.loser_race})
