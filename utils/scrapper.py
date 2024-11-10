import asyncio
import logging
import traceback
from typing import Optional, Tuple
from logger import logger
from fake_useragent import UserAgent
from response import error_response_model, success_response_model
from utils.settings import settings
from twocaptcha import TwoCaptcha
import requests
from requests.exceptions import RequestException, Timeout
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from fastapi import status


class Scrapper:
    def __init__(self, proxy: Optional[str] = None):
        logger.success("0.0 Process | Initiating Scrapper Class On Selenium")
        # self.proxy = "212.83.143.103:50365"
        print("proxy from class", proxy)
        if proxy:
            self.proxy = proxy
        self.running = True
        self.captcha_retry_attempts = 3
        self.retry_attempts = 3  # Max retry Attempts

    def chrome_options(self):
        options = Options()
        # chrome_options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--user-agent={UserAgent(os='android').random}")
        options.add_argument(f"--proxy-server={self.proxy}")
        return options

    def _is_page_loaded(self):
        """Check if the page is fully loaded."""
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            return False

    def _reload_page_with_retry(self):
        """Try to reload the page up to the retry limit if the proxy or page loading fails."""
        for attempt in range(1, self.retry_attempts + 1):
            try:
                logger.success(f"1.1 Attempt {attempt} to load the page.")
                self.driver = webdriver.Chrome(options=self.chrome_options())
                self.wait = WebDriverWait(self.driver, timeout=10)
                self.driver.get("https://www.preventivass.it/dati-principali")

                if self._is_page_loaded():
                    logger.success("1.2 Page loaded successfully.")
                    return True
                else:
                    raise TimeoutException("Page not loaded within timeout.")
            except (TimeoutException, WebDriverException, Exception) as e:
                logger.warning(f"Load attempt {attempt} failed: {e}")
                if attempt < self.retry_attempts:
                    print("Retrying...")
                    asyncio.sleep(2)  # Wait before retrying
                else:
                    logger.warning("Failed to load the page after multiple attempts.")
                    return False
        return False

    def _check_element(self, descriptor, xlocator: str, timeout: float = 0.2):
        """Checks if a element is present by the specified xPATH locator."""
        try:
            custom_wait = WebDriverWait(self.driver, timeout=timeout)
            return custom_wait.until(
                EC.presence_of_element_located((By.XPATH, xlocator))
            )
        except:
            logger.error(
                f"Element Activity | Description: {descriptor} | Error: {traceback.format_exc()}"
            )
            return False

    def _click_button(
        self, descriptor: str, xlocator: Tuple[str, str] = (By.ID, "NextButton")
    ):
        """Clicks a button located by the specified locator."""
        try:
            button = self._check_element(descriptor=descriptor, xlocator=xlocator)
            print("button text", button.text)
            self.driver.execute_script("arguments[0].scrollIntoViewIfNeeded();", button)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            self.driver.execute_script("arguments[0].disabled = false;", button)
            self.driver.execute_script("arguments[0].click();", button)
            self.driver.implicitly_wait(1)
            return True
        except Exception as e:
            logging.error(f"Button Activity | Description: {descriptor} | Error: {e}")
            return False

    def solve_captcha(self, descriptor, xlocator):
        # Retry captcha frame if any issues occur
        def restart_captcha_frame():
            logger.info("Reloading captcha frame...")
            self.driver.refresh()
            self.driver.switch_to.default_content()
            self.start()

        try:
            # Find reCAPTCHA frame and switch to it
            recaptcha_frame = self._check_element(
                descriptor="iFrame of Captcha", xlocator=xlocator, timeout=15
            )
            self.driver.switch_to.frame(recaptcha_frame)

            # Check for reCAPTCHA checkbox presence

            if self._check_element(
                "reCAPTCHA Checkbox",
                "//div[@class='recaptcha-checkbox-checkmark']",
                timeout=20,
            ):
                # Extract reCAPTCHA data using injected script
                self.driver.execute_script(settings.FIND_RECAPTCHA_SCRIPT)
                self.driver.implicitly_wait(2)
                recaptcha_data = self.driver.execute_script(
                    "return windows.findRecaptchaClients();"
                )
                logger.info(f"reCAPTCHA data found: {recaptcha_data}")

                if (
                    recaptcha_data
                    and isinstance(recaptcha_data, list)
                    and len(recaptcha_data) > 0
                ):
                    captcha_info = recaptcha_data[0]
                    logger.info(f"reCAPTCHA info found: {captcha_info}")

                    # Initialize 2Captcha solver and use sitekey
                    solver = TwoCaptcha(settings.APIKEY_2CAPTCHA)
                    result = solver.solve_captcha(
                        site_key=captcha_info["sitekey"],
                        page_url=captcha_info.get("pageurl", self.driver.current_url),
                    )

                    logger.success(f"Solved captcha: {result}")
                    return result
                else:
                    logger.warning("Failed to retrieve reCAPTCHA data. Retrying...")
                    restart_captcha_frame()
            else:
                logger.warning("reCAPTCHA checkbox not found. Retrying...")
                restart_captcha_frame()

        except Exception as e:
            logger.error(
                f"Captcha Activity | Description: {descriptor} | Error: {traceback.format_exc()}"
            )
            restart_captcha_frame()

    # Check proxy validity with requests
    def check_proxy(self):
        if self.proxy:
            # only continue code, if proxy is et
            try:
                # Set up the proxy and timeout
                proxies = {"http": self.proxy, "https": self.proxy}
                response = requests.get(
                    "http://ip-api.com/json", proxies=proxies, timeout=5
                )

                # Check if proxy worked
                if response.status_code == 200:
                    data = response.json()
                    print("Proxy is valid. IP data:", data)
                    return True
                else:
                    print("Proxy is invalid. Status code:", response.status_code)
                    return False
            except (RequestException, Timeout) as e:
                print(f"Proxy check failed: {e}")
                return False
        else:
            # return True, if there is no proxy with request
            return True

    def start(self):
        logger.success("1.0 Process | Starting Driver")
        # check proxy validity
        if self.check_proxy():
            if not self._reload_page_with_retry():
                logger.error("Page Activity | Unable to load page, closing driver.")
                self.driver.quit()
                return
            # Wait for and click the consent button if the page is loaded
            self._click_button(
                descriptor="Consent Button",
                xlocator="//button[.//span[text()=' Acconsento ']]",
            )
            # Solve Captcha
            self.solve_captcha(
                descriptor="Solving Recaptcha",
                xlocator="//iframe[contains(@title, 'reCAPTCHA')]",
            )
            return success_response_model(
                {"code": status.HTTP_200_OK, "message": "Your ID to receive the data"}
            )
        else:
            return error_response_model(
                {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Proxy is invalid. Try another",
                }
            )


BotScrapper = Scrapper
