from django.contrib import admin
from django.forms import BaseInlineFormSet
from django.forms import ModelForm

from haleygg.models import Match
from haleygg.models import Map
from haleygg.models import League
from haleygg.models import Player
from haleygg.models import Profile


class PlayerInlineFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()

        if self.errors:
            return self.errors

        profiles = []
        win_state_count = 0

        for form in self.forms:
            profile = form.cleaned_data["profile"]
            if profile in profiles:
                form.add_error("profile", "중복된 플레이어입니다.")
            profiles.append(profile)

            if form.cleaned_data["win_state"]:
                win_state_count += 1

        players_count = len(self.forms)

        if players_count != win_state_count * 2:
            for form in self.forms:
                form.add_error("win_state", "승리한 플레이어를 정확하게 선택해주세요.")

        if players_count % 2 == 1:
            self.forms[-1].add_error(None, "플레이어 수가 홀수 입니다.")
        elif players_count < 2:
            self.forms[-1].add_error(None, "최소 2명 이상의 플레이어가 있어야 합니다.")

    def save(self, commit=True):
        instances = super().save(commit=commit)
        if instances:
            if len(instances) == 2:
                instances[0].opponent = instances[1]
                instances[1].opponent = instances[0]
                instances[0].save()
                instances[1].save()
            else:
                self.instance.save()
        return instances


class PlayerInline(admin.TabularInline):
    model = Player
    extra = 0
    min_num = 2
    max_num = 8
    formset = PlayerInlineFormset
    fieldsets = [
        ("Players", {"fields": ["profile", "race", "win_state"]}),
    ]

    def has_add_permission(self, request, obj):
        if obj:
            return False
        return True

    def has_delete_permission(self, request, obj):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("profile")


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
    inlines = [PlayerInline]
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
            .prefetch_related("players", "players__profile")
        )


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "favorate_race", "joined_date")


admin.site.register(League)
admin.site.register(Map)
admin.site.register(Match, MatchAdmin)
admin.site.register(Player)
admin.site.register(Profile, ProfileAdmin)
