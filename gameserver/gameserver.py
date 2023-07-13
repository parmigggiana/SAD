from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, Response
from flagids import flagIds

app = FastAPI()


@app.put("/flags")
def check_flags():
    pass


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
