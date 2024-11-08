import sys
import requests
from loguru import logger
from utils.settings import settings

TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"


def send_log_to_telegram(message):
    try:
        response = requests.post(
            TELEGRAM_API_URL,
            data={"chat_id": settings.CHAT_ID, "text": f"{message}"},
        )
        if response.status_code != 200:
            logger.error(f"Failed to send log to Telegram: {response.text}")
    except Exception as e:
        logger.error(f"Failed to send log to Telegram: {e}")


def logging_setup():
    format_info = "<green>{time:HH:mm:ss.SS}</green> | <blue>{level}</blue> | <level>{message}</level>"
    logger.remove()

    logger.add(sys.stdout, colorize=True, format=format_info, level="INFO")
    logger.add(
        "bot.log",
        rotation="50 MB",
        compression="zip",
        format=format_info,
        level="TRACE",
    )
    if settings.USE_TG_BOT:
        print("sending to telegram")
        logger.add(
            lambda msg: send_log_to_telegram(msg),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="INFO",
        )


logging_setup()
