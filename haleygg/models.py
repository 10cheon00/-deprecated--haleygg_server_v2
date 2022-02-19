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


class League(models.Model):
    name = models.CharField(default="", max_length=30, unique=True, verbose_name="이름")
    k_factor = models.IntegerField(default=32)
    is_elo_rating_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # To avoid circular dependency.
        from elo.models import Elo

        super().save(*args, **kwargs)

        profiles = Profile.objects.all()
        Elo.objects.bulk_create(
            [Elo(profile=profile, league=self) for profile in profiles]
        )


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

    objects = models.Manager()
    statistics = MatchStatisticsQueryset.as_manager()

    class Meta:
        ordering = ["-date", "-league", "-title"]
        unique_together = ("league", "title")

    def __str__(self):
        return f"Date: {self.date}, League: {self.league_id}, Title: {self.title}, Map: {self.map_id}"

    def get_related_player_tuples(self):
        return self.player_tuples.all()


class PlayerTuple(models.Model):
    RACE_LIST = [("P", "Protoss"), ("T", "Terran"), ("Z", "Zerg")]
    match = models.ForeignKey(
        Match, on_delete=models.CASCADE, related_name="player_tuples"
    )
    winner = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="winner", verbose_name="승리자"
    )
    loser = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="loser", verbose_name="패배자"
    )
    winner_race = models.CharField(
        choices=RACE_LIST, default="", max_length=10, verbose_name="승리자 종족"
    )
    loser_race = models.CharField(
        choices=RACE_LIST, default="", max_length=10, verbose_name="승리자 종족"
    )

    def __str__(self):
        return f"Match: {self.match} Winner: {self.winner} ({self.winner_race}) Loser: {self.loser} ({self.loser_race})"
