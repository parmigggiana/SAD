from typing import Any, Literal, Optional

from icecream import ic
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# Connect to MongoDB
client: MongoClient = MongoClient("mongo", 27017)
db = client["pwnic"]


def saveFlag(
    flag: str, service: str, team: str, flagId: Optional[dict] = None
) -> Literal["Duplicate Flag", "Refused", "Accepted"]:
    try:
        res = db.flags.insert_one(
            {"_id": flag, "flagId": flagId, "service": service, "team": team}
        )
    except DuplicateKeyError:
        return "Duplicate Flag"
    except Exception as e:
        ic(e)
        return "Refused"
    return "Accepted"


def claimFlag(
    flag: str, token: str
) -> Literal["Flag already claimed", "Error", "Accepted"]:
    try:
        db.claims.insert_one({"_id": {"flag": flag, "token": token}})
    except DuplicateKeyError:
        return "Flag already claimed"
    except Exception as e:
        ic(e)
        return "Error"
    return "Accepted"


def getFlagIds(
    service: Optional[str] = None, team: Optional[str] = None
) -> dict[str, dict[str, Any]]:
    if service is None and team is None:
        filter = {}
    elif service is None:
        filter = {"team": team}
    elif team is None:
        filter = {"service": service}
    else:
        filter = {"team": team, "service": service}

    result = db.flags.find(
        filter=filter,
        projection={"_id": False, "service": True, "flagId": True, "team": True},
    )

    flagIds: dict = {}
    for row in result:
        try:
            flagIds[row["service"]][row["team"]] = row["flagId"]
        except KeyError:
            flagIds[row["service"]] = {row["team"]: row["flagId"]}

    return flagIds


def getServices() -> list[str]:
    result = db.flags.find(
        filter={},
        projection={"_id": False, "service": True, "flagId": False, "team": False},
    ).distinct("service")
    return list(result)


def getTeams() -> list[str]:
    result = db.flags.find(
        filter={},
        projection={"_id": False, "service": False, "flagId": False, "team": True},
    ).distinct("team")
    return list(result)
