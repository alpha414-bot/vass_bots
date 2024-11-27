import time
import os
import requests
from settings import emblem, settings
from utils.views import PrepData
from logger import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from fake_useragent import UserAgent
from requests.exceptions import RequestException, Timeout
from selenium.webdriver.remote.webdriver import WebDriver


# Task Worker Function
def bot_task(driver, task_id):
    logger.success(f"0.0 Task with TID: {task_id} started.")
    # Simulate the bot's work (replace with your automation logic)
    PrepData(driver=driver, task_id=task_id).get_botid()
    time.sleep(5)  # Task duration
    logger.success(f"0.1 Task with TID: {task_id} completed.")


def start_chrome() -> WebDriver:
    # Check proxy validity with requests
    def check_proxy():
        # only continue code, if proxy is et
        try:
            # Set up the proxy and timeout
            proxy = f"socks4://{settings.PROXY}"
            proxies = {"http": proxy, "https": proxy}
            if settings.USE_PROXY or not not proxy:
                response = requests.get(
                    "http://ip-api.com/json", proxies=proxies, timeout=20
                )
            else:
                response = requests.get("http://ip-api.com/json", timeout=5)

            # Check if proxy worked
            if response.status_code == 200:
                data = response.json()
                if data.get("countryCode", "").lower() == "it":
                    # Check if proxy country is pointed to "Italy"
                    return {
                        "status": True,
                        "message": "Proxy is active",
                        "proxy": proxy,
                    }
                else:
                    # Proxy country is not italy
                    logger.error(
                        f"PreTask | Proxy is in the wrong country. Current [{data.get('countryCode', '')}] instead of [IT]"
                    )
                    return {
                        "status": False,
                        "message": f"Current Proxy is in wrong country. Current [{data.get('countryCode', '')}] instead of [IT]",
                    }
            else:
                logger.error(
                    f"PreTask | Proxy check failed: status code is not status.HTTP_200_OK"
                )
                return {
                    "status": False,
                    "message": "Proxy request failed. Please try again",
                }
        except (RequestException, Timeout, Exception) as e:
            logger.error(f"PreTask | Proxy check failed {e}")
            return {
                "status": False,
                "message": "Proxy usage failed, Please try another.",
            }

    # Chrome Options
    def chrome_options():
        options = Options()
        options.add_experimental_option("detach", True)
        # options.add_argument("--headless")
        # options.add_argument("--disable-gpu")  # Applicable on Windows
        profile_path = f"{os.getcwd()}/Profile"
        os.makedirs(profile_path, exist_ok=True)
        options.add_argument(f"user-data-dir={profile_path}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--user-agent={UserAgent(os='windows').random}")
        # Remote Hub
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        if not not settings.PROXY and not not settings.USE_PROXY:
            options.add_argument(f"--proxy-server=socks4://{settings.PROXY}")
        return options

    # webdriver.Remote(
    #     command_executor="http://localhost:4444/wd/hub", options=chrome_options()
    # )
    while not check_proxy().get("status", False):
        time.sleep(15)
        check_proxy()
    return webdriver.Chrome(options=chrome_options())


# Worker Thread Function
def worker():
    print(emblem)
    MAX_WORKERS = 10  # Maximum number of concurrent tasks
    task_id = 1  # Initialize the task ID
    driver = start_chrome()

    # Use a single ThreadPoolExecutor for efficiency
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # List to keep track of running futures
        futures = []

        while True:
            # Submit a new task
            logger.success(f"TID: {task_id} | Worker service initialized")
            futures.append(
                executor.submit(
                    bot_task,
                    driver,
                    task_id,
                )
            )

            # Check completed futures
            for future in as_completed(futures):
                try:
                    future.result()  # Ensure exceptions are raised here if any
                except Exception as exc:
                    logger.error(f"VERY VERY FATAL ERROR | An error occurred: {exc}")
                finally:
                    # Remove completed future from the list
                    futures.remove(future)

            task_id += 1  # Increment task ID for the next submission


if __name__ == "__main__":
    worker()
