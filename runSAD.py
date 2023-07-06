import json


# Parse configs

with open("config.json", "r") as fs:
    config: dict = json.load(fs)
