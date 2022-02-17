from django.contrib import auth
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


@method_decorator(csrf_protect, name="dispatch")
class SignInView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        data = self.request.data

        username = data["username"]
        password = data["password"]

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return Response(status=200)
        return Response(status=2000)


@method_decorator(csrf_protect, name="dispatch")
class SignUpView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        data = self.request.data
        username = data["username"]
        password = data["password"]

        if User.objects.filter(username=username).exists():
            return Response({"error": "already exists username."})

        User.objects.create_user(username=username, password=password)
        return Response({"success": "User object created."})


@method_decorator(csrf_protect, name="dispatch")
class SignOutView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            auth.logout(request=request)
            return Response({"success": "logout"})
        except Exception as e:
            return Response({"error": f"Error msg : {e}"})


@method_decorator(ensure_csrf_cookie, name="dispatch")
class GetCSRFToken(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return Response({"success": "true"})
