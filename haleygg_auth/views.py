from rest_framework_simplejwt.views import TokenObtainPairView

from haleygg_auth.serializers import UserNameTokenObtainPairSerializer


class UserNameTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserNameTokenObtainPairSerializer
