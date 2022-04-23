from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from haleygg.tests.mixins import HaleyggUrlPatternsTestMixin


class LeagueTest(APITestCase, HaleyggUrlPatternsTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.league = {"name": "Sample league", "type": "starleague"}
        cls.url = reverse("league-list")

    def test_create_a_league(self):
        response = self.client.post(self.url, self.league)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_league_with_unique_constraint(self):
        response = self.client.post(self.url, self.league)

        response = self.client.post(self.url, self.league)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        another_league = {"name": "Another league"}
        response = self.client.post(self.url, another_league)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_leagues(self):
        self.client.post(self.url, self.league)

        self.league["name"] = "Another league"
        self.client.post(self.url, self.league)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_a_league(self):
        self.client.post(self.url, self.league)

        response = self.client.get(
            reverse("league-detail", kwargs={"name__iexact": self.league["name"]})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.league["name"])

    def test_retrieve_starleague_leagues(self):
        self.client.post(self.url, self.league)
        another_league = {"name": "Another league", "type": "proleague"}
        self.client.post(self.url, another_league)
        response = self.client.get(self.url, data={"type": "starleague"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_a_league_using_uppercase_name(self):
        self.client.post(self.url, self.league)

        response = self.client.get(
            reverse(
                "league-detail", kwargs={"name__iexact": self.league["name"].upper()}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.league["name"])

    def test_update_a_league(self):
        self.client.post(self.url, self.league)

        self.league["name"] = "Updated league"
        response = self.client.put(
            reverse("league-detail", kwargs={"name__iexact": "Sample League"}),
            self.league,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy_a_league(self):
        self.client.post(self.url, self.league)

        response = self.client.delete(
            reverse("league-detail", kwargs={"name__iexact": self.league["name"]})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
