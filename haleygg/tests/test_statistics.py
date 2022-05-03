from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from haleygg.tests.mixins import HaleyggUrlPatternsTestMixin


class StatisticsTest(APITestCase, HaleyggUrlPatternsTestMixin):
    def setUp(self):
        self.url = reverse("matches-summary")

        self.leagues = [
            {"name": "League1", "type": "proleague"},
            {"name": "League2", "type": "starleague"},
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
                        "winner": self.players[2],
                        "winner_race": "Z",
                        "loser": self.players[3],
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
                        "winner": self.players[3],
                        "winner_race": "P",
                        "loser": self.players[0],
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
                "title": "Match 5",
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
                "title": "Match 6",
                "date": "2022-01-01",
                "player_tuples": [
                    {
                        "winner": self.players[2],
                        "loser": self.players[0],
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

    def test_retrieve_statistics(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.data,
            {
                "protoss_wins_to_terran_count": 1,
                "protoss_wins_to_zerg_count": 1,
                "terran_wins_to_protoss_count": 1,
                "terran_wins_to_zerg_count": 0,
                "zerg_wins_to_protoss_count": 0,
                "zerg_wins_to_terran_count": 1,
            },
        )

    def test_retrieve_statistics_with_query_parameters(self):
        response = self.client.get(self.url, {"league": self.leagues[1]["name"]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.data,
            {
                "protoss_wins_to_terran_count": 1,
                "protoss_wins_to_zerg_count": 0,
                "terran_wins_to_protoss_count": 0,
                "terran_wins_to_zerg_count": 0,
                "zerg_wins_to_protoss_count": 0,
                "zerg_wins_to_terran_count": 1,
            },
        )

    def test_retrieve_map_statistics(self):
        response = self.client.get(self.url, {"map": self.maps[0]["name"]})
        self.assertDictEqual(
            response.data,
            {
                "protoss_wins_to_terran_count": 0,
                "protoss_wins_to_zerg_count": 0,
                "terran_wins_to_protoss_count": 1,
                "terran_wins_to_zerg_count": 0,
                "zerg_wins_to_protoss_count": 0,
                "zerg_wins_to_terran_count": 1,
                "total_matches_count": 2,
            },
        )

    def test_retrieve_map_statistics_with_query_parameters(self):
        response = self.client.get(
            self.url, {"league": self.leagues[0]["name"], "map": self.maps[0]["name"]}
        )
        self.assertDictEqual(
            response.data,
            {
                "protoss_wins_to_terran_count": 0,
                "protoss_wins_to_zerg_count": 0,
                "terran_wins_to_protoss_count": 1,
                "terran_wins_to_zerg_count": 0,
                "zerg_wins_to_protoss_count": 0,
                "zerg_wins_to_terran_count": 0,
                "total_matches_count": 1,
            },
        )

    def test_retrieve_player_statistics(self):
        response = self.client.get(self.url, {"player": self.players[0]})
        self.assertDictEqual(
            response.data,
            {
                "protoss_wins_to_protoss_count": 0,
                "protoss_wins_to_terran_count": 0,
                "protoss_wins_to_zerg_count": 0,
                "protoss_loses_to_protoss_count": 0,
                "protoss_loses_to_terran_count": 0,
                "protoss_loses_to_zerg_count": 0,
                "terran_wins_to_protoss_count": 1,
                "terran_wins_to_terran_count": 0,
                "terran_wins_to_zerg_count": 0,
                "terran_loses_to_protoss_count": 1,
                "terran_loses_to_terran_count": 0,
                "terran_loses_to_zerg_count": 0,
                "zerg_wins_to_protoss_count": 0,
                "zerg_wins_to_terran_count": 0,
                "zerg_wins_to_zerg_count": 0,
                "zerg_loses_to_protoss_count": 0,
                "zerg_loses_to_terran_count": 0,
                "zerg_loses_to_zerg_count": 0,
                "winning_melee_matches_count": 1,
                "losing_melee_matches_count": 1,
                "winning_top_and_bottom_matches_count": 1,
                "losing_top_and_bottom_matches_count": 1,
            },
        )

    def test_retrieve_player_statistics_with_query_parameters(self):
        response = self.client.get(
            self.url, {"player": self.players[0], "map": self.maps[0]["name"]}
        )
        self.assertDictEqual(
            response.data,
            {
                "protoss_wins_to_protoss_count": 0,
                "protoss_wins_to_terran_count": 0,
                "protoss_wins_to_zerg_count": 0,
                "protoss_loses_to_protoss_count": 0,
                "protoss_loses_to_terran_count": 0,
                "protoss_loses_to_zerg_count": 0,
                "terran_wins_to_protoss_count": 1,
                "terran_wins_to_terran_count": 0,
                "terran_wins_to_zerg_count": 0,
                "terran_loses_to_protoss_count": 0,
                "terran_loses_to_terran_count": 0,
                "terran_loses_to_zerg_count": 0,
                "zerg_wins_to_protoss_count": 0,
                "zerg_wins_to_terran_count": 0,
                "zerg_wins_to_zerg_count": 0,
                "zerg_loses_to_protoss_count": 0,
                "zerg_loses_to_terran_count": 0,
                "zerg_loses_to_zerg_count": 0,
                "winning_melee_matches_count": 1,
                "losing_melee_matches_count": 0,
                "winning_top_and_bottom_matches_count": 1,
                "losing_top_and_bottom_matches_count": 0,
            },
        )
