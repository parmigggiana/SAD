import random
import string
import sys

import requests

valid_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def add_flag(target_ip: str):
    flag = generate_flag()
    user = generate_user()

    requests.get(
        f"http://{target_ip}:5000/addFlag", params={"user": user, "flag": flag}
    )


def generate_flag() -> str:
    return "".join(random.choices(valid_chars, k=31)) + "="


def generate_user() -> str:
    return "".join(random.choices(string.ascii_letters, k=random.randint(8, 12)))
