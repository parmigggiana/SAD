from fastapi import FastAPI

app = FastAPI()
flagsDB = "valid_flags.txt"


@app.get("/addFlag")
def addFlag(user: str, flag: str):
    with open(flagsDB, "a") as fs:
        flag = flag.strip()
        fs.write(user + "\t" + flag + "\n")
        return f"Saved flag {flag} from user {user}"


@app.get("/flags")
def getFlags() -> list[str]:
    with open(flagsDB, "r") as fs:
        flags = fs.readlines()
        return [f.strip() for f in flags]


@app.get("/test")
def test():
    return {"response": "It works~"}
