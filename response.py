from fastapi.responses import JSONResponse
from fastapi import status
import requests
import json
from logger import logger


def success_response_model(data, record=True):
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

        if response.status_code == 200:
            return JSONResponse(
                status_code=data.get("code", 401),
                content={
                    "success": True,
                    **{k: v for k, v in data.items() if k not in {"code", "headers"}},
                },
                headers=data.get("headers", {}),
            )
    logger.error(
        f"SUCCESS | Not Recording Data OR Data Failed to send to mobility | Mobility API Response: {response.get('text', '')}"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": True,
            **{k: v for k, v in data.items() if k not in {"code", "headers"}},
        },
    )


def error_response_model(data, record=True):
    # Send Data To Mobility
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

        if response.status_code == 200:
            return JSONResponse(
                status_code=data.get("code", 401),
                content={
                    "error": True,
                    **{k: v for k, v in data.items() if k not in {"code", "headers"}},
                    "status": 5,
                },
                headers=data.get("headers", {}),
            )
    logger.error(
        f"ERROR | Not Recording Data OR Data Failed to send to mobility | Mobility API Response: {response.get('text', '')}"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            **{k: v for k, v in data.items() if k not in {"code", "headers"}},
            "status": 5,
        },
    )
