from pymongo import MongoClient
from icecream import ic
from pymongo.errors import DuplicateKeyError

# Connect to MongoDB
client = MongoClient("mongo", 27017)


def saveFlag(flag: str, service: str, flagId: dict | None = None):
    db = client["pwnic"]
    collection = db["flags"]
    try:
        res = collection.insert_one({"_id": flag, "service": service, "flagId": flagId})
    except DuplicateKeyError:
        return "Duplicate Flag"
    except Exception as e:
        ic(e)
        return "Refused"
    return "Accepted"
