from typing import Annotated, Literal, Optional

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, Response

app = FastAPI()
import db
from fastapi import FastAPI, Header

tags_metadata = [
    {
        "name": "addFlag",
        "description": """The request body must be a json-encoded dictionary, with at least the keys `flag` and `service`.
        Any other key-value pair will be added to the database in the `flagId` field""",
    },
]


validFlagResponse = Literal["Flag already claimed", "Error", "Accepted"]


app = FastAPI(openapi_tags=tags_metadata)


@app.put("/flags")
async def claim_flags(
    flags_json: Request, x_team_token: Annotated[str, Header()]
) -> JSONResponse:
    flags: list = await flags_json.json()

    if not isinstance(flags, list):
        return JSONResponse(f"`flags` should be a list, not a {type(flags)}", 422)

    response: dict[str, validFlagResponse] = {}
    for flag in flags:
        r: validFlagResponse = db.claimFlag(flag, x_team_token)
        response[flag] = r

    return JSONResponse(response, 200)


@app.get("/flagIds")
def get_flag_ids(
    service: Optional[str] = None, team_id: Optional[str] = None
) -> JSONResponse:
    if service is None and team_id is None:
        return JSONResponse(
            content={
                "Error": "Please specify a service or a team_id (or both)",
                "Valid Services": db.getServices(),
                "Valid Teams": db.getTeams(),
            },
            status_code=200,
        )

    flagIds = db.getFlagIds(service, team_id)
    return JSONResponse(flagIds, 200)


@app.post("/addFlag", tags=["addFlag"])
async def add_flag(form_json: Request) -> JSONResponse:
    form: dict = await form_json.json()
    try:
        flag: str = form.pop("flag")
        service: str = form.pop("service")
        team: str = form.pop("team")
    except KeyError:
        return JSONResponse(
            {"Error": "The request must contain `flag`, `service` and `team`"}, 422
        )

    flagId = form
    result = db.saveFlag(flag, service, team, flagId)

    return JSONResponse({"flag": flag, "service": service, "Response": result}, 200)
