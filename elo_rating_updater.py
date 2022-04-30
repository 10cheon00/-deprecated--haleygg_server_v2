import json
import requests


url = "https://haleygg.10cheon00.xyz/"
credential = {"username": "Staff", "password": "haleyggstaff"}
serialized_data = json.dumps(obj=credential, ensure_ascii=False)

response = requests.post(
    headers={"Content-Type": "application/json"},
    url=url + "api/auth/token/",
    data=serialized_data.encode("utf-8"),
)
token = json.loads(response._content)
access_token = token["access"]

response = requests.post(
    headers={
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {access_token}",
    },
    url=url + "api/elo/update/",
)
