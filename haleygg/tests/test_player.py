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

    def test_create_a_player_using_invalid_joined_date(self):
        self.player["joined_date"] = "9999-99-99"
        response = self.client.post(self.url, self.player)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.player["joined_date"] = "19-01-01"
        response = self.client.post(self.url, self.player)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_a_player_using_invalid_race(self):
        self.player["favorate_race"] = "A"
        response = self.client.post(self.url, self.player)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_players_using_conflicts_names(self):
        response = self.client.post(self.url, self.player)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.url, self.player)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_players(self):
        self.client.post(self.url, self.player)
        self.player["name"] = "Another Player"
        self.client.post(self.url, self.player)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 1)

    def test_retrieve_a_player_detail(self):
        response = self.client.post(self.url, self.player)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(
            reverse("player-detail", kwargs={"name__iexact": self.player["name"]})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.player["name"])

    def test_retrieve_player_detail_using_uppercase_name(self):
        response = self.client.post(self.url, self.player)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(
            reverse(
                "player-detail", kwargs={"name__iexact": self.player["name"].upper()}
            )
        )
        self.assertEqual(response.data["name"], self.player["name"])

    def test_update_a_player(self):
        self.client.post(self.url, self.player)

        player = {"name": "Updated Player", "favorate_race": "Z"}
        response = self.client.put(
            reverse("player-detail", kwargs={"name__iexact": self.player["name"]}),
            player,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy_a_player(self):
        self.client.post(self.url, self.player)

        response = self.client.delete(
            reverse("player-detail", kwargs={"name__iexact": self.player["name"]}),
            self.player,
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
