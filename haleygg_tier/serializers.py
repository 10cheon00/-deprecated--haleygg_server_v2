from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_str
from rest_framework import serializers

from haleygg.models import League
from haleygg.models import Player
from haleygg_tier.models import PlayerTier


class CaseInsensitiveSlugRelatedField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            return queryset.get(**{f"{self.slug_field}__iexact": str(data)})
        except ObjectDoesNotExist:
            self.fail(
                "does_not_exist", slug_name=self.slug_field, value=smart_str(data)
            )
        except (TypeError, ValueError):
            self.fail("invalid")


class PlayerTierSerializer(serializers.ModelSerializer):
    league = CaseInsensitiveSlugRelatedField(
        queryset=League.objects.all(), slug_field="name"
    )
    player = CaseInsensitiveSlugRelatedField(
        queryset=Player.objects.all(), slug_field="name"
    )

    class Meta:
        model = PlayerTier
        fields = ("league", "player", "tier")
