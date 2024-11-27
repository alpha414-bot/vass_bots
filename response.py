from fastapi.responses import JSONResponse
from fastapi import status
import requests
import json


def success_response_model(data, record=True):
    data = {
        **{k: v for k, v in data.items() if k not in {"code", "headers"}},
        "status": 1,
    }
    print("Success Response", data)
    response = {}

    if record:
        # Send Data To Mobility
        response = requests.request(
            "POST",
            "https://mobilityexpress.it/api/sendData",
            headers={"Content-Type": "application/json"},
            data=json.dumps(data),
            timeout=50,
        )

        if str(response.status_code) == "200":
            print("partial response", response.text)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=data,
            )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=data,
    )


def error_response_model(data, record=True):
    # Send Data To Mobility
    data = {
        **{k: v for k, v in data.items() if k not in {"code", "headers"}},
        "status": 4,
    }
    print("Error Response", data)
    response = {}
    if record:
        response = requests.request(
            "POST",
            "https://mobilityexpress.it/api/sendData",
            headers={"Content-Type": "application/json"},
            data=json.dumps(data),
            timeout=50,
        )

        if str(response.status_code) == "200":
            print("partial response", response.text)
            return JSONResponse(
                status_code=data.get("code", 401),
                content=data,
                headers=data.get("headers", {}),
            )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=data,
    )
