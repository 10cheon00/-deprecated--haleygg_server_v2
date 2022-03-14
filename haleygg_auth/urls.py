from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView

from haleygg_auth.views import UserNameTokenObtainPairView


urlpatterns = [
    path("token/", UserNameTokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("token/verify/", TokenVerifyView.as_view()),
]
