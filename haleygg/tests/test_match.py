from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from haleygg.tests.mixins import HaleyggUrlPatternsTestMixin


class MatchTestCase(APITestCase, HaleyggUrlPatternsTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.league = {"name": "Sample League"}
        cls.map = {"name": "Sample Map"}
        cls.players = [
            {"name": "Sample Player 1"},
            {"name": "Sample Player 2"},
            {"name": "Sample Player 3"},
            {"name": "Sample Player 4"},
            {"name": "Sample Player 5"},
            {"name": "Sample Player 6"},
        ]

    def setUp(self):
        self.client.post(reverse("league-list"), self.league)
        self.client.post(reverse("map-list"), self.map)
        for i in range(len(self.players)):
            self.client.post(reverse("player-list"), self.players[i])

        self.url = reverse("match-list")
        self.match = {
            "date": "2022-01-01",
            "league": self.league["name"],
            "title": "Sample Match",
            "map": self.map["name"],
            "player_tuples": [
                {
                    "winner": self.players[0]["name"],
                    "loser": self.players[1]["name"],
                    "winner_race": "T",
                    "loser_race": "T",
                }
            ],
        }

    def test_create_a_melee_match_no_using_player_tuples(self):
        self.match["player_tuples"] = []

        response = self.client.post(self.url, self.match)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_a_melee_match(self):
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_a_top_and_bottom_match(self):
        self.match["player_tuples"] = [
            {"winner": self.players[0]["name"], "loser": self.players[1]["name"]},
            {"winner": self.players[2]["name"], "loser": self.players[3]["name"]},
            {"winner": self.players[4]["name"], "loser": self.players[5]["name"]},
        ]

        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_a_match_using_an_non_existent_map(self):
        map_name = "Not existent map"
        self.match["map"] = map_name

        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(
            reverse("map-detail", kwargs={"name__iexact": "Not existent map"}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], map_name)

    def test_create_a_match_using_an_non_existent_player(self):
        pass

    def test_create_matches(self):
        pass

    def test_create_matches_using_conflicts_fields(self):
        pass
