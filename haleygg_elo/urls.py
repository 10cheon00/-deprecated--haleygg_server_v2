from django.urls import path

from haleygg_elo.views import EloListView
from haleygg_elo.views import EloRankingView
from haleygg_elo.views import EloUpdateView


urlpatterns = [
    path("", EloListView.as_view()),
    path("ranking/", EloRankingView.as_view()),
    path("update/", EloUpdateView.as_view()),
]
