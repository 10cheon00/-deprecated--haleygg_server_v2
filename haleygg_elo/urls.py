from django.urls import path

from haleygg_elo.views import EloHistoryView
from haleygg_elo.views import EloRankingView


urlpatterns = [
    path("ranking/", EloRankingView.as_view()),
    path("history/", EloHistoryView.as_view()),
]
