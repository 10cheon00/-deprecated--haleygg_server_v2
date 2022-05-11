from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from haleygg_tier.models import PlayerTier
from haleygg_tier.serializers import PlayerTierSerializer


class PlayerTierViewSet(ModelViewSet):
    serializer_class = PlayerTierSerializer
    queryset = PlayerTier.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()

        player_name = self.request.query_params.get("player")
        if player_name:
            queryset = queryset.filter(player__name__iexact=player_name)

        return queryset

    def create(self, request, *args, **kwargs):
        try:
            is_many = isinstance(request.data, list)
            if not is_many:
                return super().create(request=request, args=args, kwargs=kwargs)

            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except IntegrityError as e:
            detail = str(e).partition("DETAIL:  ")[2]
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": detail})
