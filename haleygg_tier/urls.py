from django.urls import path

from haleygg_tier.views import PlayerTierListView
from haleygg_tier.views import PlayerTierCreateView

from haleygg_tier.views import PlayerTierRetrieveUpdateDestroyView

urlpatterns = [
    path("", PlayerTierCreateView.as_view()),
    path("players/<str:player>/", PlayerTierListView.as_view()),
    path(
        "players/<str:player>/leagues/<str:league>/",
        PlayerTierRetrieveUpdateDestroyView.as_view(),
    ),
]
