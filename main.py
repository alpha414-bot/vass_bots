import json
import traceback
from fastapi.encoders import jsonable_encoder
from logger import logger
import requests
from database import get_db
from response import error_response_model
from utils.schemas import RawRequestData, RequestData
from utils.settings import settings, emblem
from fastapi import FastAPI, status
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import Depends
from utils.views import start_prep_data


app = FastAPI()

# Add CORS middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.post("/quote/price")
def get_quote_price(
    requestData: RequestData,
    db: Session = Depends(get_db),
):
    data = {}

    try:
        payload = json.dumps(requestData.dict())
        headers = {"Content-Type": "application/json"}
        response = requests.request(
            "POST",
            "https://mobilityexpress.it/api/getplatetest",
            headers=headers,
            data=payload,
            timeout=2,
        )
        if response.status_code == 200:
            data = json.loads(response.text)
            if data.get("status", None) != "1":
                raise ValueError(response.text)
            else:
                data = RawRequestData(
                    proxy=requestData.proxy,
                    request_id=requestData.request_id,
                    request_refresh=requestData.request_refresh,
                    **json.loads(response.text),
                )
                return start_prep_data(data=data, db=db)
        else:
            raise ValueError(
                json.dumps(
                    jsonable_encoder(
                        {
                            "status": 500,
                            "message": "Bad request. Please try with another data or try again later",
                        }
                    )
                )
            )
    except Exception as e:
        try:
            return error_response_model(
                {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "payload": requestData.dict(),
                    **json.loads(str(e)),
                }
            )
        except Exception as e:
            logger.error(
                f"Fatal Error | Error: {e} | Traceback: {traceback.format_exc()}"
            )
            return error_response_model(
                {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": "Fatal Server Error",
                }
            )


if __name__ == "__main__":
    import uvicorn

    print(emblem)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8085,
        reload=True,
        access_log=True,
        reload_includes=["*.py", ".env"],
        reload_excludes=["call.py"],
    )
