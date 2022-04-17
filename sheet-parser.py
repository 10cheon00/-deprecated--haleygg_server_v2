import json
import requests


credential = {"username": "Staff", "password": "haleyggstaff"}
serialized_data = json.dumps(obj=credential, ensure_ascii=False)
response = requests.post(
    headers={"Content-Type": "application/json"},
    url="https://haleygg.10cheon00.xyz/api/auth/token/",
    data=serialized_data.encode("utf-8"),
)
token = json.loads(response._content)
access_token = token["access"]


def get_data_from_json(sheet_name):
    with open("./sample.json") as f:
        sheets = json.loads(f.read())
        return sheets[sheet_name]


def parse_match_information(row, league_name):
    league = league_name
    title = row["경기명"]
    index = title.find(league_name) + len(league_name)
    title = title[index + 1 :]
    return {
        "date": ("20" + row["일자"]).replace(".", "-"),
        "league": league,
        "title": title,
        "map": row["Map"],
        "player_tuples": [],
    }


def parse_melee_matches(sheet_data, league_name):
    parsed_result = []
    sheet_length = len(sheet_data)
    index = 0
    while index < sheet_length:
        row = sheet_data[index]

        index += 2
        if row["기타"] is not None:
            continue

        parsed_data = parse_match_information(row=row, league_name=league_name)
        if row["ID"] == row["A"]:
            winner = row["A"]
            winner_race = row["A종족"]
            loser = row["B"]
            loser_race = row["B종족"]
        else:
            winner = row["B"]
            winner_race = row["B종족"]
            loser = row["A"]
            loser_race = row["A종족"]

        parsed_data["player_tuples"] = [
            {
                "winner": winner,
                "winner_race": winner_race,
                "loser": loser,
                "loser_race": loser_race,
            }
        ]
        parsed_result.append(parsed_data)

    return parsed_result


def parse_top_and_bottom_matches(sheet_data, league_name):
    parsed_result = []
    sheet_length = len(sheet_data)
    index = 0
    while index < sheet_length:
        row = sheet_data[index]

        player_count = (
            (row["A1"] is not None)
            + (row["A2"] is not None)
            + (row["A3"] is not None)
            + (row["B1"] is not None)
            + (row["B2"] is not None)
            + (row["B3"] is not None)
        )
        index += player_count
        if row["기타"] is not None:
            continue

        parsed_data = parse_match_information(row=row, league_name=league_name)

        if row["ID"] == row["A1"]:
            player_tuples = [
                {"winner": row["A1"], "loser": row["B1"]},
                {"winner": row["A2"], "loser": row["B2"]},
            ]
            if row["A3"] is not None:
                player_tuples.append({"winner": row["A3"], "loser": row["B3"]})
        else:
            player_tuples = [
                {"winner": row["B1"], "loser": row["A1"]},
                {"winner": row["B2"], "loser": row["A2"]},
            ]
            if row["B3"] is not None:
                player_tuples.append({"winner": row["B3"], "loser": row["A3"]})

        parsed_data["player_tuples"] = player_tuples
        parsed_result.append(parsed_data)

    return parsed_result


def parse(league_name, type=None):
    sheet_name = league_name
    if type is not None:
        sheet_name += f"::{type}"

    data = get_data_from_json(sheet_name=sheet_name)

    if type == "팀플":
        parsed_data = parse_top_and_bottom_matches(
            sheet_data=data, league_name=league_name
        )
    else:
        parsed_data = parse_melee_matches(sheet_data=data, league_name=league_name)

        serialized_data = json.dumps(obj=parsed_data, ensure_ascii=False)

        response = requests.post(
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {access_token}",
            },
            url="https://haleygg.10cheon00.xyz/api/matches/",
            data=serialized_data.encode("utf-8"),
        )
        print(league_name, response)


parse(league_name="HPL S1", type="개인")
parse(league_name="HPL S1", type="팀플")
parse(league_name="HPL S2", type="개인")
parse(league_name="HPL S2", type="팀플")
parse(league_name="HSL S1")
parse(league_name="HPL S3", type="개인")
parse(league_name="HPL S3", type="팀플")
parse(league_name="HSL S2")
parse(league_name="HPL S4", type="개인")
parse(league_name="HPL S4", type="팀플")
parse(league_name="HSL S3")
parse(league_name="HSL S4")
parse(league_name="HPL S5", type="개인")
parse(league_name="HPL S5", type="팀플")
parse(league_name="HSL S5")
parse(league_name="HPL S6", type="개인")
parse(league_name="HPL S6", type="팀플")
parse(league_name="HPL S7", type="개인")
parse(league_name="HPL S7", type="팀플")
parse(league_name="HPL S8", type="개인")
parse(league_name="HPL S8", type="팀플")
parse(league_name="HSL S6")
parse(league_name="HPL S9", type="개인")
parse(league_name="HPL S9", type="팀플")
