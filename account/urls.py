from django.urls import path

from account.views import GetCSRFToken
from account.views import SignInView
from account.views import SignOutView
from account.views import SignUpView


urlpatterns = [
    path("csrf-cookie/", GetCSRFToken.as_view()),
    path("signup/", SignUpView.as_view()),
    path("signin/", SignInView.as_view()),
    path("signout/", SignOutView.as_view()),
]
