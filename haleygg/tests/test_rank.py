from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RankTest(APITestCase):
    def setUp(self):
        self.url = reverse("ranks")
        self.leagues = [
            {"name": "League1", "type": "proleague"},
            {"name": "League2", "type": "proleague"},
        ]
        self.client.post(reverse("league-list"), self.leagues[0])
        self.client.post(reverse("league-list"), self.leagues[1])

        self.maps = [{"name": "Map1"}, {"name": "Map2"}]
        self.client.post(reverse("map-list"), self.maps[0])
        self.client.post(reverse("map-list"), self.maps[1])

        self.players = [
            "player1",
            "player2",
            "player3",
            "player4",
        ]

        self.melee_matches = [
            {
                "league": self.leagues[0]["name"],
                "map": self.maps[0]["name"],
                "title": "Match 1",
                "date": "2022-01-01",
                "player_tuples": [
                    {
                        "winner": self.players[0],
                        "winner_race": "T",
                        "loser": self.players[1],
                        "loser_race": "P",
                    }
                ],
            },
            {
                "league": self.leagues[0]["name"],
                "map": self.maps[1]["name"],
                "title": "Match 2",
                "date": "2022-01-01",
                "player_tuples": [
                    {
                        "winner": self.players[1],
                        "winner_race": "P",
                        "loser": self.players[2],
                        "loser_race": "Z",
                    }
                ],
            },
            {
                "league": self.leagues[1]["name"],
                "map": self.maps[0]["name"],
                "title": "Match 3",
                "date": "2022-01-01",
                "player_tuples": [
                    {
                        "winner": self.players[1],
                        "winner_race": "Z",
                        "loser": self.players[0],
                        "loser_race": "T",
                    }
                ],
            },
            {
                "league": self.leagues[1]["name"],
                "map": self.maps[1]["name"],
                "title": "Match 4",
                "date": "2022-01-01",
                "player_tuples": [
                    {
                        "winner": self.players[0],
                        "winner_race": "P",
                        "loser": self.players[1],
                        "loser_race": "T",
                    }
                ],
            },
            {
                "league": self.leagues[0]["name"],
                "map": self.maps[0]["name"],
                "title": "Match 5",
                "date": "2022-01-01",
                "player_tuples": [
                    {
                        "winner": self.players[1],
                        "winner_race": "P",
                        "loser": self.players[2],
                        "loser_race": "T",
                    }
                ],
            },
        ]
        self.client.post(reverse("match-list"), self.melee_matches, format="json")

        self.top_and_bottom_matches = [
            {
                "league": self.leagues[0]["name"],
                "map": self.maps[0]["name"],
                "title": "Match 6",
                "date": "2022-01-01",
                "player_tuples": [
                    {
                        "winner": self.players[0],
                        "loser": self.players[2],
                    },
                    {
                        "winner": self.players[1],
                        "loser": self.players[3],
                    },
                ],
            },
            {
                "league": self.leagues[0]["name"],
                "map": self.maps[1]["name"],
                "title": "Match 7",
                "date": "2022-01-01",
                "player_tuples": [
                    {
                        "winner": self.players[0],
                        "loser": self.players[3],
                    },
                    {
                        "winner": self.players[2],
                        "loser": self.players[1],
                    },
                ],
            },
            {
                "league": self.leagues[1]["name"],
                "map": self.maps[0]["name"],
                "title": "Match 8",
                "date": "2022-01-01",
                "player_tuples": [
                    {
                        "winner": self.players[1],
                        "loser": self.players[0],
                    },
                    {
                        "winner": self.players[3],
                        "loser": self.players[2],
                    },
                ],
            },
            {
                "league": self.leagues[1]["name"],
                "map": self.maps[1]["name"],
                "title": "Match 9",
                "date": "2022-01-01",
                "player_tuples": [
                    {
                        "winner": self.players[2],
                        "loser": self.players[0],
                    },
                    {
                        "winner": self.players[1],
                        "loser": self.players[3],
                    },
                ],
            },
            {
                "league": self.leagues[0]["name"],
                "map": self.maps[0]["name"],
                "title": "Match 10",
                "date": "2022-01-01",
                "player_tuples": [
                    {
                        "winner": self.players[0],
                        "loser": self.players[2],
                    },
                    {
                        "winner": self.players[3],
                        "loser": self.players[1],
                    },
                ],
            },
        ]
        self.client.post(
            reverse("match-list"), self.top_and_bottom_matches, format="json"
        )

    def test_retrieve_total_melee_matches_count_rank(self):
        query_params = {"match_type": "melee"}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 5},
                {"name": "player1", "value": 3},
                {"name": "player3", "value": 2},
            ],
        )

    def test_retrieve_total_melee_matches_count_rank_with_query_parameters(self):
        query_params = {"match_type": "melee", "league": self.leagues[0]["name"]}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 3},
                {"name": "player3", "value": 2},
                {"name": "player1", "value": 1},
            ],
        )

        query_params = {"match_type": "melee", "map": self.maps[0]["name"]}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 3},
                {"name": "player1", "value": 2},
                {"name": "player3", "value": 1},
            ],
        )

        query_params = {"match_type": "melee", "league__type": "proleague"}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 5},
                {"name": "player1", "value": 3},
                {"name": "player3", "value": 2},
            ],
        )

    def test_retrieve_win_melee_matches_count_rank(self):
        query_params = {"match_type": "melee", "category": "win"}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 3},
                {"name": "player1", "value": 2},
            ],
        )

    def test_retrieve_win_melee_matches_count_rank_with_query_parameters(self):
        query_params = {
            "match_type": "melee",
            "category": "win",
            "league": self.leagues[0]["name"],
        }
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 2},
                {"name": "player1", "value": 1},
            ],
        )

        query_params = {
            "match_type": "melee",
            "category": "win",
            "map": self.maps[0]["name"],
        }
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 2},
                {"name": "player1", "value": 1},
            ],
        )

        query_params = {
            "match_type": "melee",
            "category": "win",
            "league__type": "proleague",
        }
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 3},
                {"name": "player1", "value": 2},
            ],
        )

    def test_retrieve_lose_melee_matches_count_rank(self):
        query_params = {"match_type": "melee", "category": "lose"}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 2},
                {"name": "player3", "value": 2},
                {"name": "player1", "value": 1},
            ],
        )

    def test_retrieve_lose_melee_matches_count_rank_with_query_parameters(self):
        query_params = {
            "match_type": "melee",
            "category": "lose",
            "league": self.leagues[0]["name"],
        }
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player3", "value": 2},
                {"name": "player2", "value": 1},
            ],
        )

        query_params = {
            "match_type": "melee",
            "category": "lose",
            "map": self.maps[0]["name"],
        }
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player1", "value": 1},
                {"name": "player2", "value": 1},
                {"name": "player3", "value": 1},
            ],
        )

        query_params = {
            "match_type": "melee",
            "category": "lose",
            "league__type": "proleague",
        }
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 2},
                {"name": "player3", "value": 2},
                {"name": "player1", "value": 1},
            ],
        )

    def test_retrieve_total_top_and_bottom_matches_rank(self):
        query_params = {"match_type": "top_and_bottom"}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player1", "value": 5},
                {"name": "player2", "value": 5},
                {"name": "player3", "value": 5},
                {"name": "player4", "value": 5},
            ],
        )

    def test_retrieve_total_top_and_bottom_matches_rank_with_query_parameters(self):
        query_params = {
            "match_type": "top_and_bottom",
            "league": self.leagues[0]["name"],
        }
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player1", "value": 3},
                {"name": "player2", "value": 3},
                {"name": "player3", "value": 3},
                {"name": "player4", "value": 3},
            ],
        )

        query_params = {
            "match_type": "top_and_bottom",
            "map": self.maps[0]["name"],
        }
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player1", "value": 3},
                {"name": "player2", "value": 3},
                {"name": "player3", "value": 3},
                {"name": "player4", "value": 3},
            ],
        )
        query_params = {
            "match_type": "top_and_bottom",
            "league__type": "proleague",
        }
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player1", "value": 5},
                {"name": "player2", "value": 5},
                {"name": "player3", "value": 5},
                {"name": "player4", "value": 5},
            ],
        )

    def test_retrieve_win_top_and_bottom_matches_rank(self):
        query_params = {"match_type": "top_and_bottom", "category": "win"}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player1", "value": 3},
                {"name": "player2", "value": 3},
                {"name": "player3", "value": 2},
                {"name": "player4", "value": 2},
            ],
        )

    def test_retrieve_win_top_and_bottom_matches_rank_with_query_parameters(self):
        query_params = {
            "match_type": "top_and_bottom",
            "category": "win",
            "league": self.leagues[0]["name"],
        }
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player1", "value": 3},
                {"name": "player2", "value": 1},
                {"name": "player3", "value": 1},
                {"name": "player4", "value": 1},
            ],
        )

        query_params = {
            "match_type": "top_and_bottom",
            "category": "win",
            "map": self.maps[0]["name"],
        }
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player1", "value": 2},
                {"name": "player2", "value": 2},
                {"name": "player4", "value": 2},
            ],
        )

        query_params = {
            "match_type": "top_and_bottom",
            "category": "win",
            "league__type": "proleague",
        }
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player1", "value": 3},
                {"name": "player2", "value": 3},
                {"name": "player3", "value": 2},
                {"name": "player4", "value": 2},
            ],
        )

    def test_retrieve_lose_top_and_bottom_matches_rank(self):
        query_params = {"match_type": "top_and_bottom", "category": "lose"}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player3", "value": 3},
                {"name": "player4", "value": 3},
                {"name": "player1", "value": 2},
                {"name": "player2", "value": 2},
            ],
        )

    def test_retrieve_lose_top_and_bottom_matches_rank_with_query_parameters(self):
        query_params = {
            "match_type": "top_and_bottom",
            "category": "lose",
            "league": self.leagues[0]["name"],
        }
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 2},
                {"name": "player3", "value": 2},
                {"name": "player4", "value": 2},
            ],
        )

        query_params = {
            "match_type": "top_and_bottom",
            "category": "lose",
            "map": self.maps[0]["name"],
        }
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player3", "value": 3},
                {"name": "player1", "value": 1},
                {"name": "player2", "value": 1},
                {"name": "player4", "value": 1},
            ],
        )

        query_params = {
            "match_type": "top_and_bottom",
            "category": "lose",
            "league__type": "proleague",
        }
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player3", "value": 3},
                {"name": "player4", "value": 3},
                {"name": "player1", "value": 2},
                {"name": "player2", "value": 2},
            ],
        )

    def test_retrieve_total_matches_rank(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 10},
                {"name": "player1", "value": 8},
                {"name": "player3", "value": 7},
                {"name": "player4", "value": 5},
            ],
        )

    def test_retrieve_total_matches_rank_with_query_parameters(self):
        query_params = {"league": self.leagues[0]["name"]}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 6},
                {"name": "player3", "value": 5},
                {"name": "player1", "value": 4},
                {"name": "player4", "value": 3},
            ],
        )

        query_params = {"map": self.maps[0]["name"]}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 6},
                {"name": "player1", "value": 5},
                {"name": "player3", "value": 4},
                {"name": "player4", "value": 3},
            ],
        )

        query_params = {"league__type": "proleague"}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 10},
                {"name": "player1", "value": 8},
                {"name": "player3", "value": 7},
                {"name": "player4", "value": 5},
            ],
        )

    def test_retrieve_win_matches_rank(self):
        query_params = {"category": "win"}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 6},
                {"name": "player1", "value": 5},
                {"name": "player3", "value": 2},
                {"name": "player4", "value": 2},
            ],
        )

    def test_retrieve_win_matches_rank_with_query_parameters(self):
        query_params = {"category": "win", "league": self.leagues[0]["name"]}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player1", "value": 4},
                {"name": "player2", "value": 3},
                {"name": "player3", "value": 1},
                {"name": "player4", "value": 1},
            ],
        )

        query_params = {"category": "win", "map": self.maps[0]["name"]}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 4},
                {"name": "player1", "value": 3},
                {"name": "player4", "value": 2},
            ],
        )

        query_params = {"category": "win", "league__type": "proleague"}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player2", "value": 6},
                {"name": "player1", "value": 5},
                {"name": "player3", "value": 2},
                {"name": "player4", "value": 2},
            ],
        )

    def test_retrieve_lose_matches_rank(self):
        query_params = {"category": "lose"}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player3", "value": 5},
                {"name": "player2", "value": 4},
                {"name": "player1", "value": 3},
                {"name": "player4", "value": 3},
            ],
        )

    def test_retrieve_lose_matches_rank_with_query_parameters(self):
        query_params = {"category": "lose", "league": self.leagues[0]["name"]}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player3", "value": 4},
                {"name": "player2", "value": 3},
                {"name": "player4", "value": 2},
            ],
        )

        query_params = {"category": "lose", "map": self.maps[0]["name"]}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player3", "value": 4},
                {"name": "player1", "value": 2},
                {"name": "player2", "value": 2},
                {"name": "player4", "value": 1},
            ],
        )

        query_params = {"category": "lose", "league__type": "proleague"}
        response = self.client.get(self.url, data=query_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data,
            [
                {"name": "player3", "value": 5},
                {"name": "player2", "value": 4},
                {"name": "player1", "value": 3},
                {"name": "player4", "value": 3},
            ],
        )
