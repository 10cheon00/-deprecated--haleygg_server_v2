from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from haleygg_tier.models import PlayerTier
from haleygg_tier.serializers import PlayerTierSerializer


class PlayerTierCreateView(CreateAPIView):
    serializer_class = PlayerTierSerializer
    queryset = PlayerTier.objects.all()

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


class PlayerTierListView(ListAPIView):
    serializer_class = PlayerTierSerializer

    def get_queryset(self):
        queryset = PlayerTier.objects.all()
        player_name = self.kwargs["player"]

        if player_name:
            queryset = queryset.filter(player__name__iexact=player_name)

        return queryset


class PlayerTierRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = PlayerTierSerializer
    queryset = PlayerTier.objects.all()
    lookup_fields = ["league", "player"]

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        filter = {}
        for field in self.lookup_fields:
            filter[f"{field}__name__iexact"] = self.kwargs[field]

        return get_object_or_404(queryset, **filter)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError as e:
            detail = str(e).partition("DETAIL:  ")[2]
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": detail})
