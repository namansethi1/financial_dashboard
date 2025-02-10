import json

with open("secrets.json", "r") as file:
    secrets = json.load(file)

ALPHA_VANTAGE_API_KEY = secrets["ALPHA_VANTAGE_API_KEY"]
