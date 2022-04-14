from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from haleygg.tests.mixins import HaleyggUrlPatternsTestMixin


class PlayerTestCase(APITestCase, HaleyggUrlPatternsTestMixin):
    def setUp(self):
        self.player = {"name": "Sample Player"}
        self.url = reverse("player-list")

    def test_create_a_player(self):
        response = self.client.post(self.url, self.player)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_a_player_using_invalid_race(self):
        self.player["favorate_race"] = "R"
        response = self.client.post(self.url, self.player)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_players_using_conflicts_names(self):
        response = self.client.post(self.url, self.player)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.url, self.player)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_player_detail_using_name_lookup_field(self):
        response = self.client.post(self.url, self.player)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(
            reverse("player-detail", kwargs={"name__iexact": self.player["name"]})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.player["name"])

    def test_get_player_detail_using_case_insensitive_name_lookup_field(self):
        response = self.client.post(self.url, self.player)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(
            reverse(
                "player-detail", kwargs={"name__iexact": self.player["name"].upper()}
            )
        )
        self.assertEqual(response.data["name"], self.player["name"])
