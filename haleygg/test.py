from django.urls import include
from django.urls import path
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import URLPatternsTestCase


class HaleyggUrlPatternsTestMixin(URLPatternsTestCase):
    urlpatterns = [path("api/", include("haleygg.urls"))]


class LeagueTest(APITestCase, HaleyggUrlPatternsTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.league = {"name": "Sample League"}
        cls.url = reverse("league-list")

    def test_create_a_league(self):
        response = self.client.post(self.url, self.league)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        another_league = {
            "name": "Another League",
            "k_factor": 30,
            "is_elo_rating_active": True,
        }
        response = self.client.post(self.url, another_league)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_league_using_conflicts_names(self):
        response = self.client.post(self.url, self.league)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.url, self.league)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_leagues(self):
        response = self.client.post(self.url, self.league)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.league["name"] = "Another League"
        response = self.client.post(self.url, self.league)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

        response = self.client.get(
            reverse("league-detail", kwargs={"name__iexact": "Another League"})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Another League")

    def test_retrieve_leagues_only_elo_rating_active_is_true(self):
        another_league = {"name": "Another League", "is_elo_rating_active": True}
        self.client.post(self.url, self.league)
        self.client.post(self.url, another_league)

        response = self.client.get(
            reverse("league-list"), {"is_elo_rating_active": True}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_a_league(self):
        self.client.post(self.url, self.league)

        self.league["name"] = "Updated League"
        self.league["k_factor"] = 30
        self.league["is_elo_rating_active"] = True
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
