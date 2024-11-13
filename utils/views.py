import traceback
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from logger import logger
from response import error_response_model, success_response_model
from fastapi import status
from utils.models import QuoteData
from .schemas import RawRequestData
from .scrapper import BotScrapper


def start_prep_data(data: RawRequestData, db: Session):
    try:
        logger.success(
            f"0.1 Task | Cleaning & Processing & Preping Request Data | Proxy: {data.proxy}"
        )
        if data.request_id and not data.refresh:
            # accessing already store data and data.refresh is none
            quote = (
                db.query(QuoteData)
                .filter(
                    (QuoteData.id == data.request_id)
                    & (QuoteData.response_data.isnot(None))
                    & (QuoteData.response_data != "")
                )
                .first()
            )
            if quote:
                quote_response_data = {
                    **jsonable_encoder(quote.response_data),
                    "request_id": quote.id,
                }
                return success_response_model(
                    {
                        "code": status.HTTP_200_OK,
                        "request_id": quote.id,
                        "data": quote_response_data,
                    }
                )

        else:
            # create a new processing quote data
            return BotScrapper(data, db).start()
    except Exception as e:
        logger.error(
            f"Error occurred >>> {e} ::::-> __TRACEBACK__ {traceback.format_exc()} <<<"
        )
        return error_response_model(
            {
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Internal Server Error.",
            }
        )
