import traceback

from fastapi import BackgroundTasks
from requests import Session
from logger import logger
from utils.schemas import RawRequestData


def start_prep_data(
    data: RawRequestData, background_tasks: BackgroundTasks, db: Session
):
    try:
        logger.error(f"Task | Cleaning & Processing & Preping Data")
        return
    except Exception as e:
        logger.error("Error occurred", e, traceback.format_exc())
