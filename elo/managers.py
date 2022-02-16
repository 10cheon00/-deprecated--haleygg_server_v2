from django.db.models import F
from django.db.models import Manager
from django.db.models import QuerySet
from django.db.models import Sum


class EloRankingQuerySet(QuerySet):
    def get_ranking(self):
        return (
            self.values("player__profile__name")
            .annotate(value=Sum("value"))
            .values("value", name=F("player__profile__name"))
            .order_by(F("value").desc())
        )


class EloFilterQuerySet(QuerySet):
    def get_queryset_related_profile(self, profile):
        return (
            self.filter(player__profile=profile)
            .order_by(F("player__match__date").desc())
            .values("value", date=F("player__match__date"))
        )
