from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from haleygg.tests.mixins import HaleyggUrlPatternsTestMixin


class MatchTestCase(APITestCase, HaleyggUrlPatternsTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.league = {"name": "Sample league"}
        cls.another_league = {"name": "Another league"}

        cls.map = {"name": "Sample map"}
        cls.another_map = {"name": "Another map"}

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
        self.client.post(reverse("league-list"), self.another_league)
        self.client.post(reverse("map-list"), self.map)
        self.client.post(reverse("map-list"), self.another_map)
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
                    "loser_race": "Z",
                }
            ],
        }
        self.matches = [
            {
                "date": "2000-1-1",
                "league": self.league["name"],
                "title": "Sample Match 1",
                "map": self.another_map["name"],
                "player_tuples": [
                    {
                        "winner": self.players[0]["name"],
                        "winner_race": "T",
                        "loser": self.players[1]["name"],
                        "loser_race": "R",
                    }
                ],
            },
            {
                "date": "2000-1-1",
                "league": self.another_league["name"],
                "title": "Sample Match 2",
                "map": self.another_map["name"],
                "player_tuples": [
                    {
                        "winner": self.players[2]["name"],
                        "winner_race": "P",
                        "loser": self.players[3]["name"],
                        "loser_race": "R",
                    }
                ],
            },
            {
                "date": "2000-1-1",
                "league": self.another_league["name"],
                "title": "Sample Match 3",
                "map": self.map["name"],
                "player_tuples": [
                    {
                        "winner": self.players[4]["name"],
                        "winner_race": "Z",
                        "loser": self.players[5]["name"],
                        "loser_race": "P",
                    }
                ],
            },
        ]

    def test_create_a_melee_match(self):
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_a_match_without_league(self):
        self.match["league"] = None
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.match["league"] = ""
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_a_match_without_title(self):
        self.match["title"] = None
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.match["title"] = ""
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_a_match_without_date(self):
        self.match["date"] = None
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.match["date"] = ""
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_a_match_with_invalid_date(self):
        self.match["date"] = "2000-1-32"
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.match["date"] = "20-1-1"
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.match["date"] = "2000.1.1"
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_a_match_without_map(self):
        self.match["map"] = None
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.match["map"] = ""
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_a_match_with_map_that_does_not_exist(self):
        map_name = "Not existent map"
        self.match["map"] = map_name

        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(
            reverse("map-detail", kwargs={"name__iexact": map_name}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], map_name)

    def test_create_a_match_without_player_tuples(self):
        self.match["player_tuples"] = None
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.match["player_tuples"] = []
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.match["player_tuples"] = [
            {
                "winner": None,
                "winner_race": None,
                "loser": None,
                "loser_race": None,
            }
        ]
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_a_match_with_player_that_does_not_exist(self):
        self.match["player_tuples"][0] = {
            "winner": "Non-existent Player 1",
            "winner_race": "T",
            "loser": "Non-existent Player 2",
            "loser_race": "P",
        }
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(
            reverse("player-detail", kwargs={"name__iexact": self.players[2]["name"]})
        )
        self.assertEqual(response.data["name"], self.players[2]["name"])
        response = self.client.get(
            reverse("player-detail", kwargs={"name__iexact": self.players[3]["name"]})
        )
        self.assertEqual(response.data["name"], self.players[3]["name"])

    def test_create_a_match_with_invalid_player_race_in_player_tuples(self):
        self.match["player_tuples"][0]["winner_race"] = "A"
        self.match["player_tuples"][0]["loser_race"] = "T"
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.match["player_tuples"][0]["winner_race"] = "T"
        self.match["player_tuples"][0]["loser_race"] = "A"
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_a_melee_match_without_player_race_in_player_tuples(self):
        self.match["player_tuples"][0]["winner_race"] = ""
        self.match["player_tuples"][0]["loser_race"] = "T"
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.match["player_tuples"][0]["winner_race"] = "T"
        self.match["player_tuples"][0]["loser_race"] = ""
        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_a_top_and_bottom_match(self):
        self.match["player_tuples"] = [
            {"winner": self.players[0]["name"], "loser": self.players[1]["name"]},
            {"winner": self.players[2]["name"], "loser": self.players[3]["name"]},
            {"winner": self.players[4]["name"], "loser": self.players[5]["name"]},
        ]

        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_a_top_and_bottom_match_with_non_existent_players_in_player_tuples(
        self,
    ):
        self.match["player_tuples"] = [
            {"winner": "Non-existent player 1", "loser": "Non-existent player 2"},
            {"winner": "Non-existent player 3", "loser": "Non-existent player 4"},
            {"winner": "Non-existent player 5", "loser": "Non-existent player 6"},
        ]

        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(
            reverse("player-detail", kwargs={"name__iexact": "Non-existent player 1"})
        )
        self.assertEqual(response.data["name"], "Non-existent player 1")
        response = self.client.get(
            reverse("player-detail", kwargs={"name__iexact": "Non-existent player 2"})
        )
        self.assertEqual(response.data["name"], "Non-existent player 2")
        response = self.client.get(
            reverse("player-detail", kwargs={"name__iexact": "Non-existent player 3"})
        )
        self.assertEqual(response.data["name"], "Non-existent player 3")
        response = self.client.get(
            reverse("player-detail", kwargs={"name__iexact": "Non-existent player 4"})
        )
        self.assertEqual(response.data["name"], "Non-existent player 4")
        response = self.client.get(
            reverse("player-detail", kwargs={"name__iexact": "Non-existent player 5"})
        )
        self.assertEqual(response.data["name"], "Non-existent player 5")
        response = self.client.get(
            reverse("player-detail", kwargs={"name__iexact": "Non-existent player 6"})
        )
        self.assertEqual(response.data["name"], "Non-existent player 6")

    def test_create_a_top_and_bottom_match_with_corrupted_player_tuples(self):
        self.match["player_tuples"] = [
            {"winner": self.players[0]["name"], "loser": self.players[1]["name"]},
            {"winner": None, "loser": self.players[3]["name"]},
            {"winner": self.players[4]["name"], "loser": None},
        ]

        response = self.client.post(self.url, self.match, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_matches_on_single_request(self):
        response = self.client.post(self.url, self.matches, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_matches_with_conflicts_fields(self):
        conflict_match = {
            "date": "9999-12-31",
            "map": "Other Map",
            "league": self.match["league"],
            "title": self.match["title"],
            "player_tuples": self.match["player_tuples"],
        }
        matches = [self.match, conflict_match]
        response = self.client.post(self.url, matches, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_matches(self):
        self.client.post(self.url, self.matches, format="json")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data_keys = response.data.keys()
        self.assertTrue("count" in data_keys)
        self.assertTrue("next" in data_keys)
        self.assertTrue("previous" in data_keys)
        self.assertTrue("results" in data_keys)

        self.assertEqual(len(response.data["results"]), 3)

    def test_retrieve_matches_related_with_query_parameters(self):
        self.client.post(self.url, self.matches, format="json")

        response = self.client.get(
            self.url, {"league": self.another_league["name"]}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 2)

        response = self.client.get(
            self.url, {"map": self.another_map["name"]}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 2)

        response = self.client.get(
            self.url, {"players": self.players[0]["name"]}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 1)

    def test_retrieve_a_match(self):
        response = self.client.post(self.url, self.match, format="json")
        match = response.data
        response = self.client.get(reverse("match-detail", kwargs={"pk": match["id"]}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], match["id"])

    def test_update_match(self):
        response = self.client.post(self.url, self.match, format="json")
        match_id = response.data["id"]
        player_tuples_id = response.data["player_tuples"][0]["id"]

        self.match["map"] = "Non-existent map"
        self.match["date"] = "2022-12-31"
        self.match["title"] = "Updated match"
        self.match["player_tuples"] = [
            {
                "id": player_tuples_id,
                "winner": "Non-existent player 1",
                "winner_race": "Z",
                "loser": "Non-existent player 2",
                "loser_race": "Z",
            }
        ]
        response = self.client.put(
            reverse("match-detail", kwargs={"pk": match_id}), self.match, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy_match(self):
        result = self.client.post(self.url, self.match, format="json")
        created_match = result.data
        response = self.client.delete(
            reverse("match-detail", kwargs={"pk": created_match["id"]})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
