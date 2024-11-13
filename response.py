from fastapi.responses import JSONResponse


def success_response_model(data):
    return JSONResponse(
        status_code=data.get("code", 401),
        content={
            "success": True,
            **{k: v for k, v in data.items() if k not in {"code", "headers"}},
        },
        headers=data.get("headers", {}),
    )


def error_response_model(data):
    return JSONResponse(
        status_code=data.get("code", 401),
        content={
            "error": True,
            **{k: v for k, v in data.items() if k not in {"code", "headers"}},
        },
        headers=data.get("headers", {}),
    )
