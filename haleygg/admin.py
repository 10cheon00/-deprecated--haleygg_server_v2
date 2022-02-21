from django.contrib import admin
from django.forms import BaseInlineFormSet
from django.forms import ModelForm

from haleygg.models import Match
from haleygg.models import Map
from haleygg.models import League
from haleygg.models import PlayerTuple
from haleygg.models import Profile
from haleygg_elo.models import create_elo


class PlayerTupleInlineFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()

        profiles = []
        for form in self.forms:
            winner = form.cleaned_data["winner"]
            loser = form.cleaned_data["loser"]
            if winner in profiles:
                form.add_error("winner", "중복된 플레이어입니다.")
            profiles.append(winner)
            if loser in profiles:
                form.add_error("loser", "중복된 플레이어입니다.")
            profiles.append(loser)


class PlayerTupleInline(admin.TabularInline):
    model = PlayerTuple
    extra = 0
    min_num = 1
    max_num = 4
    formset = PlayerTupleInlineFormset
    fieldsets = [
        ("PlayerTuples", {"fields": ["winner", "winner_race", "loser", "loser_race"]}),
    ]

    def has_add_permission(self, request, obj):
        if obj:
            return False
        return True

    def has_delete_permission(self, request, obj):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("winner", "loser")


class MatchForm(ModelForm):
    class Meta:
        model = Match
        fields = (
            "date",
            "league",
            "title",
            "map",
            "miscellaneous",
        )


class MatchAdmin(admin.ModelAdmin):
    list_display = ("date", "league", "title", "map")
    list_select_related = ["league", "map"]
    inlines = [PlayerTupleInline]
    form = MatchForm
    fieldsets = [
        (
            "Match",
            {
                "fields": (
                    "date",
                    "league",
                    "title",
                    "map",
                    "miscellaneous",
                )
            },
        ),
    ]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("league", "map")
            .prefetch_related("player_tuples")
        )

    def save_related(self, request, form, formsets, change):
        # Override for create elo object.
        form.save_m2m()
        if change:
            # TODO
            # Update all elo after this match.
            pass
        else:
            if len(formsets) == 1:
                instance = formsets[0].save()
                create_elo(player_tuple=instance[0])


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "favorate_race", "joined_date")


admin.site.register(League)
admin.site.register(Map)
admin.site.register(Match, MatchAdmin)
admin.site.register(PlayerTuple)
admin.site.register(Profile, ProfileAdmin)
