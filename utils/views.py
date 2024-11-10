import traceback
from fastapi import BackgroundTasks
from requests import Session
from logger import logger
from .schemas import RawRequestData
from .scrapper import BotScrapper


def start_prep_data(
    data: RawRequestData, background_tasks: BackgroundTasks, db: Session
):
    try:
        logger.success(
            f"0.1 Task | Cleaning & Processing & Preping Request Data | {data.proxy}"
        )
        return BotScrapper(proxy=data.proxy).start()
    except Exception as e:
        logger.error(
            f"Error occurred >>> {e} ::::-> __TRACEBACK__ {traceback.format_exc()} <<<"
        )
