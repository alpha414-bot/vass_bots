import sys
import traceback
import requests
from loguru import logger
from settings import settings

BOTTOKEN = "7559961212:AAG2hRrH0BSAkGgdTYRpMm1Br2wNlYouNWY"


def send_log_to_telegram(message):
    if not not settings.USE_TG_BOT:
        if len(message) <= settings.MAX_TELEGRAM_MESSAGE_LENGTH:
            try:
                response = requests.post(
                    f"https://api.telegram.org/bot{BOTTOKEN}/sendMessage",
                    data={"chat_id": settings.CHAT_ID, "text": f"{message}"},
                    timeout=20,
                )
                if response.status_code != 200:
                    logger.warning(f"Failed to send log to Telegram: {response.text}")
            except Exception as e:
                logger.warning(
                    f"Failed to send log to Telegram: {traceback.format_exc()}"
                )
        else:
            logger.info("Log message is too long for Telegram, not sent.")


def logging_setup():
    format_info = "<green>{time:HH:mm:ss.SS}</green> | <blue>{level}</blue> | <level>{message}</level>"
    logger.remove()

    logger.add(sys.stdout, colorize=True, format=format_info, level="INFO")
    logger.add(
        "logs/bot.log",
        rotation="50 MB",
        compression="zip",
        format=format_info,
        level="TRACE",
    )
    logger.add(
        lambda msg: send_log_to_telegram(msg),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="TRACE",
        filter=lambda record: record["level"].name not in ["INFO", "WARNING"],
    )


logging_setup()
