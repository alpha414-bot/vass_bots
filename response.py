from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success_response_model(data, json_response: bool = True):
    if json_response:
        return JSONResponse(
            status_code=data.get("code", 401),
            content={"success": True, "data": jsonable_encoder(data, exclude={"code"})},
            headers=data.get("headers", {}),
        )
    return jsonable_encoder(
        {
            "success": True,
            "error": False,
            "data": jsonable_encoder(data, exclude={"code"}),
        }
    )


def error_response_model(data, json_response: bool = True):
    if json_response:
        return JSONResponse(
            status_code=data.get("code", 401),
            content={"error": True, "data": jsonable_encoder(data, exclude={"code"})},
            headers=data.get("headers", {}),
        )
    return jsonable_encoder(
        {
            "success": False,
            "error": True,
            "data": jsonable_encoder(data, exclude={"code"}),
        }
    )
