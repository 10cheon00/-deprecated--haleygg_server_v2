from decimal import Decimal

from django.db import models
from django.db.models import Case
from django.db.models import F
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models import Subquery
from django.db.models import When
from django.db.models.functions import Coalesce
from django.db.models.functions import Cast
from django.db.models.functions import Power

from haleygg.models import Profile
from haleygg.models import Match


class Elo(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    rating = models.DecimalField(default=1000.0, max_digits=6, decimal_places=1)
    winning_state = models.BooleanField(default=False)

    class Meta:
        ordering = "match__date", "match__league", "match__title"

    def __str__(self):
        return f"Match : {self.match_id} | {self.profile} - {self.rating}"


def create_elo_rating(player_tuple):
    if is_newest_match(match=player_tuple.match):
        previous_rating_objects = (
            Elo.objects.filter(
                Q(match__league=player_tuple.match.league)
                & (
                    Q(match__date__lt=player_tuple.match.date)
                    | (
                        Q(match__date=player_tuple.match.date)
                        & Q(match__title__lt=player_tuple.match.title)
                    )
                )
            )
            .filter(Q(profile=player_tuple.winner) | Q(profile=player_tuple.loser))
            .order_by()
            .reverse()
            .distinct("profile")
        )

        previous_rating_object_from_players = (
            Elo.objects.select_related("match", "match__league")
            .filter(match__league=OuterRef("match__league"))
            .filter(Q(profile=player_tuple.winner) | Q(profile=player_tuple.loser))
            .reverse()
        )

        calculated_rating_queryset = previous_rating_objects.annotate(
            previous_my_rating=Coalesce(
                Subquery(
                    previous_rating_object_from_players.filter(
                        profile=OuterRef("profile")
                    ).values("rating")[:1]
                ),
                1000.0,
                output_field=models.DecimalField(max_digits=6, decimal_places=1),
            ),
            previous_opponent_rating=Coalesce(
                Subquery(
                    previous_rating_object_from_players.exclude(
                        profile=OuterRef("profile")
                    ).values("rating")[:1]
                ),
                1000.0,
                output_field=models.DecimalField(max_digits=6, decimal_places=1),
            ),
            score=Case(When(profile=player_tuple.winner, then=1), default=0),
        ).annotate(
            calculated_rating=Cast(
                expression=(
                    F("previous_my_rating")
                    + F("match__league__k_factor")
                    * (
                        F("score")
                        - 1
                        / (
                            Power(
                                10,
                                (
                                    F("previous_opponent_rating")
                                    - F("previous_my_rating")
                                )
                                / 400,
                            )
                            + 1
                        )
                    )
                ),
                output_field=models.DecimalField(max_digits=6, decimal_places=1),
            )
        )
        print(calculated_rating_queryset.values())
        winner = Elo.objects.create(
            profile=player_tuple.winner,
            match=player_tuple.match,
            rating=Subquery(
                calculated_rating_queryset.filter(profile=player_tuple.winner).values(
                    "calculated_rating"
                )[:1]
            ),
            winning_state=True,
        )
        # 값이 이상하게 추가됨
        # 업데이트를 돌리면 제대로 돌아옴
        loser = Elo.objects.create(
            profile=player_tuple.loser,
            match=player_tuple.match,
            rating=Subquery(
                calculated_rating_queryset.filter(profile=player_tuple.loser).values(
                    "calculated_rating"
                )[:1]
            ),
            winning_state=False,
        )
        print(winner.__dict__)
        print(loser.__dict__)
    else:
        # TODO
        # 중간에 추가하는 과정.
        # 추가할 때 이전 ELO를 토대로 값을 생성, 그 이후는 업데이트

        # update elo objects following created elo
        update_elo_rating(player_tuple=player_tuple)


def is_newest_match(match):
    return Match.objects.filter(league=match.league).last() == match


# Pass match parameter what managing from admin or serializer.
def update_elo_rating(player_tuple):
    rating_objects = player_tuple.match.elo_set.all()
    # Update difference in profile attribute with parameter and instance.

    rating_objects.update(
        profile_id=Case(
            When(winning_state=True, then=player_tuple.winner_id),
            default=player_tuple.loser_id,
        ),
    )

    # Update rating objects related to parameter.
    update_rating_to_instance(rating_objects)

    # Update all rating objects following parameter.
    next_rating_objects = Elo.objects.filter(
        Q(match__league=player_tuple.match.league)
        & Q(match__date__gt=player_tuple.match.date)
        | (
            Q(match__date=player_tuple.match.date)
            & Q(match__title__gt=player_tuple.match.title)
        )
    )

    update_rating_to_instance(next_rating_objects)


def delete_elo():
    # 테이블에서 elo가 지워질 경우, 후행 데이터들을 업데이트해야함.
    pass


def update_rating_to_instance(queryset):
    previous_rating_objects = Elo.objects.select_related(
        "match", "match__league"
    ).filter(
        Q(match__league=OuterRef("match__league"))
        & (
            Q(match__date__lt=OuterRef("match__date"))
            | (
                Q(match__date=OuterRef("match__date"))
                & Q(match__title__lt=OuterRef("match__title"))
            )
        )
    )
    calculated_rating_queryset = (
        queryset.annotate(
            opponent=Subquery(
                queryset.filter(match=OuterRef("match"))
                .exclude(profile=OuterRef("profile"))
                .values("profile")[:1]
            ),
        )
        .annotate(
            previous_my_rating=Coalesce(
                Subquery(
                    previous_rating_objects.filter(profile=OuterRef("profile"))
                    .reverse()
                    .values("rating")[:1]
                ),
                1000.0,
                output_field=models.DecimalField(max_digits=6, decimal_places=1),
            ),
            previous_opponent_rating=Coalesce(
                Subquery(
                    previous_rating_objects.filter(profile=OuterRef("opponent"))
                    .reverse()
                    .values("rating")[:1]
                ),
                1000.0,
                output_field=models.DecimalField(max_digits=6, decimal_places=1),
            ),
            score=Case(When(winning_state=True, then=1), default=0),
        )
        .annotate(
            calculated_rating=Cast(
                expression=(
                    F("previous_my_rating")
                    + F("match__league__k_factor")
                    * (
                        F("score")
                        - 1
                        / (
                            Power(
                                10,
                                (
                                    F("previous_opponent_rating")
                                    - F("previous_my_rating")
                                )
                                / 400,
                            )
                            + 1
                        )
                    )
                ),
                output_field=models.DecimalField(max_digits=6, decimal_places=1),
            )
        )
    )

    queryset.update(
        rating=Subquery(
            calculated_rating_queryset.filter(id=OuterRef("id")).values(
                "calculated_rating"
            )[:1]
        )
    )


def calculate_elo(previous_rating_of_winner, previous_rating_of_loser, k):
    import math

    winner_expected_winning_percentage = 1 / (
        math.pow(10, (previous_rating_of_loser - previous_rating_of_winner) / 400) + 1
    )
    winner_rating = k * (1 - winner_expected_winning_percentage)
    loser_rating = -1 * winner_rating
    return (winner_rating, loser_rating)


"""
{'id': 61, 'profile_id': 1, 'match_id': 62, 'rating': Decimal('1015.1'),
 'winning_state': True, 
 'previous_my_rating': Decimal('1015.1'),
  'previous_opponent_rating': Decimal('983.8'), 
  'am_i_winner': 0,
   'calculated_rating': Decimal('998.8')
   },
 {'id': 64, 'profile_id': 3, 'match_id': 63, 'rating': Decimal('983.8'),
  'winning_state': False, 
   'previous_my_rating': Decimal('983.8'),
  'previous_opponent_rating': Decimal('1015.1'), 
  'am_i_winner': 1, 
  'calculated_rating': Decimal('1000.1')}

  {'id': 63, 'profile_id': 2, 'match_id': 63, 
  'rating': Decimal('1000.6'), 
  'winning_state': True, 
  'previous_my_rating': Decimal('1000.6'), 
  'previous_opponent_rating': Decimal('983.8'),
   'score': 0, 'calculated_rating': Decimal('984.9')}

{'id': 64, 
'profile_id': 3, 
'match_id': 63, 
'rating': Decimal('983.8'),
 'winning_state': False,
  'previous_my_rating': Decimal('999.9'),
   'previous_opponent_rating': Decimal('1000.6'), 
   'score': 1, 'calculated_rating': Decimal('1014.9')

{'id': 57, 'profile_id': 1, 'match_id': 60, 'rating': Decimal('1015.0'), 'winning_state': True, 'opponent': 2, 'previous_my_rating': Decimal('1000.0'), 'previous_opponent_rating': Decimal('1000.0'), 'score': 1, 'calculated_rating': Decimal('1015.0')}
{'id': 58, 'profile_id': 2, 'match_id': 60, 'rating': Decimal('985.0'), 'winning_state': False, 'opponent': 1, 'previous_my_rating': Decimal('1000.0'), 'previous_opponent_rating': Decimal('1000.0'), 'score': 0, 'calculated_rating': Decimal('985.0')}

{'id': 61, 'profile_id': 1, 'match_id': 62, 'rating': Decimal('1029.4'), 'winning_state': True, 'opponent': 3, 'previous_my_rating': Decimal('1015.0'), 'previous_opponent_rating': Decimal('1000.0'), 'score': 1, 'calculated_rating': Decimal('1029.4')}
{'id': 62, 'profile_id': 3, 'match_id': 62, 'rating': Decimal('985.6'), 'winning_state': False, 'opponent': 1, 'previous_my_rating': Decimal('1000.0'), 'previous_opponent_rating': Decimal('1015.0'), 'score': 0, 'calculated_rating': Decimal('985.6')}
{'id': 63, 'profile_id': 2, 'match_id': 63, 'rating': Decimal('1000.0'), 'winning_state': True, 'opponent': 3, 'previous_my_rating': Decimal('985.0'), 'previous_opponent_rating': Decimal('985.6'), 'score': 1, 'calculated_rating': Decimal('1000.0')}
{'id': 64, 'profile_id': 3, 'match_id': 63, 'rating': Decimal('970.6'), 'winning_state': False, 'opponent': 2, 'previous_my_rating': Decimal('985.6'), 'previous_opponent_rating': Decimal('985.0'), 'score': 0, 'calculated_rating': Decimal('970.6')}
{'id': 109, 'profile_id': 2, 'match_id': 92, 'rating': Decimal('1013.7'), 'winning_state': True, 'opponent': 3, 'previous_my_rating': Decimal('1000.0'), 'previous_opponent_rating': Decimal('970.6'), 'score': 1, 'calculated_rating': Decimal('1013.7')}
{'id': 110, 'profile_id': 3, 'match_id': 92, 'rating': Decimal('956.9'), 'winning_state': False, 'opponent': 2, 'previous_my_rating': Decimal('970.6'), 'previous_opponent_rating': Decimal('1000.0'), 'score': 0, 'calculated_rating': Decimal('956.9')}
{'id': 111, 'profile_id': 1, 'match_id': 94, 'rating': Decimal('1043.8'), 'winning_state': True, 'opponent': 2, 'previous_my_rating': Decimal('1029.4'), 'previous_opponent_rating': Decimal('1013.7'), 'score': 1, 'calculated_rating': Decimal('1043.7')}
{'id': 112, 'profile_id': 2, 'match_id': 94, 'rating': Decimal('1000.5'), 'winning_state': False, 'opponent': 1, 'previous_my_rating': Decimal('1013.7'), 'previous_opponent_rating': Decimal('1029.4'), 'score': 0, 'calculated_rating': Decimal('999.4')}
   
}
"""
