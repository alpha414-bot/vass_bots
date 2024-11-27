import traceback
from logger import logger
from response import error_response_model
from fastapi import status
from .schemas import RawRequestData
from .scrapper import Scrapper
from datetime import datetime
import json
import time
import requests
from settings import settings


class PrepData:
    def __init__(self, driver, task_id):
        self.bot_id = None
        self.data = None
        self.driver = driver
        self.task_id = task_id

    def get_botid(self):
        #
        logger.success(
            f"TID: {self.task_id} | 1.0 Running loop to get botid | Telegram Usage {settings.USE_TG_BOT}"
        )
        try:
            while not self.bot_id:
                botrequests = requests.request(
                    "POST",
                    "https://mobilityexpress.it/api/getidbot",
                    data=json.dumps({"idProvBot": 999969, "remoteHost": ""}),
                    headers={"Content-Type": "application/json"},
                    timeout=20,
                )
                data = json.loads(botrequests.text)
                if int(data.get("Status", 0)) == 1 and data.get("data", None):
                    start_time = datetime.now()  # Exact time bot is up and running
                    self.bot_id = data.get("data", {}).get("ID", False)
                    if self.bot_id:
                        # BotId is not null and is passed
                        return self.run_plate_and_metadata(start_time=start_time)
                time.sleep(2)  # 2 seconds sleep
        except Exception as e:
            logger.error(f"TID: {self.task_id} | 1.1 Error when running bot loop {e}")

    def run_plate_and_metadata(self, start_time=datetime):
        logger.success(
            f"TID: {self.task_id} | 2.0 Running production plate endpoint | BotID: {self.bot_id}"
        )
        data = {}
        try:
            # botrequest
            payload = json.dumps({"botId": int(self.bot_id), "remoteHost": ""})
            headers = {"Content-Type": "application/json"}
            while not self.data:
                response = requests.request(
                    "POST",
                    "https://mobilityexpress.it/api/getplate",
                    headers=headers,
                    data=payload,
                    timeout=10,
                )
                if response.status_code == 200:
                    data = json.loads(response.text)
                    if not data.get("status", None) != "1":
                        data = RawRequestData(
                            proxy=settings.PROXY,
                            **json.loads(response.text),
                        )
                        self.data = data
                        pass
            if self.data:
                return self.start_prep_data(data=self.data, start_time=start_time)
        except Exception as e:
            try:
                return error_response_model(
                    {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "",
                        **(json.loads(str(e)) if not not e else {}),
                    },
                    False,
                )
            except Exception as e:
                logger.error(
                    f"TID: {self.task_id} | Fatal Error: {e} | Traceback: {traceback.format_exc()}"
                )
                return error_response_model(
                    {
                        "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "message": e,
                        **(json.loads(str(e)) if not not e else {}),
                    },
                    False,
                )

    def start_prep_data(self, data: RawRequestData, start_time: datetime):
        try:
            logger.success(
                f"TID: {self.task_id} | 3.0 Task | Cleaning & Processing & Preping Request Data | Proxy: {data.proxy}"
            )
            # create a new processing quote data
            return Scrapper(
                data=data,
                driver=self.driver,
                start_time=start_time,
                task_id=self.task_id,
            ).start()
        except Exception as e:
            logger.error(
                f"TID: {self.task_id} | 3.1 Error occurred >>> {e} ::::-> __TRACEBACK__ {traceback.format_exc()} <<<"
            )
            return error_response_model(
                {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Internal Server Error.",
                    **(json.loads(str(e)) if not not e else {}),
                },
                False,
            )
