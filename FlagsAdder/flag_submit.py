import sys, requests, json
from typing import Iterable


def submit_flags(flags: Iterable) -> bool | None:
    """
    Returns True if flags were successfully submitted, False if we were rate limited, otherwise None
    """

    flags = list(flags)
    print(f"{flags = }")

    if not flags:
        return None

    try:
        response = requests.put(
            "http://10.10.0.1:8080/flags",
            headers={"X-Team-Token": "351ec1772465afe1cbf539e77208246f"},
            json=flags,
        )
        json.dump(response.json(), sys.stdout, indent=2)

        return "RATE_LIMIT" not in response.text

    except requests.ConnectTimeout as e:
        raise e
    except requests.JSONDecodeError as e:
        raise e
    except Exception as e:
        print(e)


if __name__ == "__main__":
    flags = ["RENU7L10KVUMPNVTJLI4F8M1GTCNBTM=", "BVJ90HTVZUNRL38YJMQXGAL3PUM2O8K="]
    submit_flags(flags)
