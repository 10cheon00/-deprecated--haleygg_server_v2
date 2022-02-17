from django.urls import path

from elo.views import EloRankingListView
from elo.views import EloDetailView


urlpatterns = [
    path("ranking/", EloRankingListView.as_view()),
    path("<int:profile>/", EloDetailView.as_view()),
]
