import random
import string

import requests

valid_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def add_flag(target_ip: str):
    flag = generate_flag()
    user = generate_user()

    data = {"flag": flag, "service": "simple_service", "team": target_ip, "user": user}
    response = requests.post(url=f"http://10.10.0.1:8080/addFlag", json=data)
    if response.json()["Response"] == "Accepted":
        requests.get(
            f"http://{target_ip}:5000/addFlag", params={"user": user, "flag": flag}
        )
        print(data)


def generate_flag() -> str:
    return "".join(random.choices(valid_chars, k=31)) + "="


def generate_user() -> str:
    return "".join(random.choices(string.ascii_letters, k=random.randint(8, 12)))


if __name__ == "__main__":
    add_flag("10.60.1.1")
