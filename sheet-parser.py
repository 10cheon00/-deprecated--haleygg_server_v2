import gspread
import json
import requests


def get_player_tuples_from_row(row):
    player_tuples = []
    if "B3" in row.keys():
        # top and bottom
        player_tuples.append(
            {
                "winner": row["Winner1"],
                "loser": row["Loser1"],
            }
        )
        player_tuples.append(
            {
                "winner": row["Winner2"],
                "loser": row["Loser2"],
            }
        )
        player_tuples.append(
            {
                "winner": row["Winner3"],
                "loser": row["Loser3"],
            }
        )
    else:
        # melee
        winner = row["Winner"]
        loser = row["Loser"]
        if row["A"] == winner:
            winner_race = row["A종족"]
            loser_race = row["B종족"]
        else:
            winner_race = row["B종족"]
            loser_race = row["A종족"]
        player_tuples.append(
            {
                "winner": winner,
                "loser": loser,
                "winner_race": winner_race,
                "loser_race": loser_race,
            }
        )
    return player_tuples


def parse_row(row, league_name):
    title = row["경기명"]
    index = title.find(league_name) + len(league_name)
    league = title[:index]
    title = title[index + 1 :]
    player_tuples = get_player_tuples_from_row(row=row)
    parsed_data = {
        "date": ("20" + row["일자"]).replace(".", "-"),
        "league": league,
        "title": title,
        "map": row["Map"],
        "player_tuples": player_tuples,
    }

    return parsed_data


def parse(league_name):
    gc = gspread.service_account(filename="api-key.json")
    docs = gc.open_by_url(
        "https://docs.google.com/spreadsheets/d/1uWSQN27VYk89oOOjMePFftAhnMZjYf5e-3BbyUrFXwA/edit?usp=sharing"
    )
    sheet = docs.worksheet("팀플전적Data")
    data = sheet.get_all_records()

    parsed_data = []
    for i in range(len(data)):
        parsed_data.append(parse_row(row=data[i], league_name=league_name))

    serialized_data = json.dumps(obj=parsed_data, ensure_ascii=False)

    requests.post(
        headers={"Content-Type": "application/json; charset=utf-8"},
        url="http://127.0.0.1:8000/api/matches/",
        data=serialized_data.encode("utf-8"),
    )


parse(league_name="HPL S1")
