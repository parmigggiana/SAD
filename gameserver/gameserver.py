from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Form, Request
from fastapi.responses import JSONResponse, Response
from flagids import flagIds
from typing import Annotated

app = FastAPI()
import db

from fastapi import FastAPI

tags_metadata = [
    {
        "name": "addFlag",
        "description": """The request body must be a json-encoded dictionary, with at least the keys `flag` and `service`.
        Any other key-value pair will be added to the database in the `flagId` field""",
    },
]

app = FastAPI(openapi_tags=tags_metadata)


@app.put("/flags")
async def claim_flags(flags_json: Request) -> JSONResponse:
    request: dict = await flags_json.json()
    flags: list = request.pop("flags")
    token: str = request.pop("token")

    if request:
        print(request)
    if not isinstance(flags, list):
        return JSONResponse(f"`flags` should be a list, not a {type(flags)}", 422)

    response = {}
    for flag in flags:
        r = db.claimFlag(flag, token)
        response += {flag: r}
    return JSONResponse(response, 200)


@app.get("/flagIds")
def get_flag_ids(service: str = "ALL", team_id: str = "ALL") -> JSONResponse:
    if service == "ALL" and team_id == "ALL":
        services = list(flagIds.keys())
        return JSONResponse(
            content={
                "Error": "Please specify a service or a team_id (or both)",
                "Valid Services": services,
                "Valid Teams": list(flagIds[services[0]].keys()),
            },
            status_code=200,
        )

    if service == "ALL":
        ret = {sid_k: sid_v[team_id] for sid_k, sid_v in flagIds.items()}

    if team_id == "ALL":
        ret = flagIds[service]

    return JSONResponse(ret, 200)


@app.post("/addFlag", tags=["addFlag"])
async def add_flag(form_json: Request) -> JSONResponse:
    form: dict = await form_json.json()
    flag: str = form["flag"]
    service: str = form["service"]
    form.pop("flag")
    form.pop("service")

    flagId = form
    result = db.saveFlag(flag, service, flagId)

    if flagId:
        return JSONResponse(
            {"flag": flag, "service": service, "flagId": flagId, "Accepted": result},
            200,
        )
    else:
        return JSONResponse({"flag": flag, "service": service, "Response": result}, 200)
