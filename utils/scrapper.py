import asyncio
import json
import re
import time
import traceback
from datetime import datetime
from fastapi import status
from fastapi.encoders import jsonable_encoder
from logger import logger
from fake_useragent import UserAgent
from response import error_response_model, success_response_model
from utils.schemas import RawRequestData
from settings import settings
from .captcha import TwoCaptcha
import requests
from requests.exceptions import RequestException, Timeout
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException


class Scrapper:
    def __init__(self, data: RawRequestData, start_time: datetime, task_id):
        logger.success(
            f"TID: {task_id} | 4.0.0 Process | Initiating Scrapper Class On Selenium"
        )
        self.task_id = task_id
        self.driver = None
        self.start_time = start_time
        proxy = data.proxy
        self.anag = data.data.anag
        self.veicolo = data.data.veicolo
        self.datiPreventivo = data.data.datiPreventivo
        self.portante = data.data.portante
        self.proxy = None
        self.captcha_token = None
        self.age = 25
        if proxy:
            self.proxy = f"socks4://{proxy}"
        self.running = True
        self.captcha_retry_attempts = 3
        self.retry_attempts = 3  # Max retry Attempts

    def chrome_options(self, proxy=None):
        options = Options()
        options.add_experimental_option("detach", True)
        # options.add_argument("--headless")
        # options.add_argument("--disable-gpu")  # Applicable on Windows
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--user-agent={UserAgent(os='windows').random}")
        # Remote Hub
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        return options

    def teardown(self):
        """Teardown method to quit the WebDriver and show a message box."""
        logger.success(f"TID: {self.task_id} | 4.8 [LAST STEP] Terminating Session")
        if hasattr(self, "driver") and self.driver:
            self.driver.close()
            self.driver.quit()
            logger.info(f"TID: {self.task_id} | Driver quit successfully.")
        else:
            logger.warning(
                f"TID: {self.task_id} | Driver does not exist or is already None."
            )
        return error_response_model(
            {
                "code": status.HTTP_400_BAD_REQUEST,
                "status": 5,
                "message": "Issue with processing request. Please try again.",
            },
            False,
        )

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
                logger.success(
                    f"TID: {self.task_id} | 4.2 Attempt [{attempt}] to load the page."
                )
                self.driver.get("https://www.preventivass.it/dati-principali")

                if self._is_page_loaded():
                    logger.success(
                        f"TID: {self.task_id} | 4.3 Page loaded successfully."
                    )
                    return True
                else:
                    raise TimeoutException("Page not loaded within timeout.")
            except (TimeoutException, WebDriverException, Exception) as e:
                logger.warning(
                    f"TID: {self.task_id} | Load attempt {attempt} failed: {e}"
                )
                if attempt < self.retry_attempts:
                    asyncio.sleep(2)  # Wait before retrying
                else:
                    logger.warning(
                        f"TID: {self.task_id} | Failed to load the page after multiple attempts."
                    )
                    return False
        return False

    def _check_element(
        self, descriptor, xlocator: str, timeout: float = 0.2, no_error: bool = False
    ):
        """Checks if a element is present by the specified xPATH locator."""
        try:
            custom_wait = WebDriverWait(self.driver, timeout=timeout)
            return custom_wait.until(
                EC.presence_of_element_located((By.XPATH, xlocator))
            )
        except Exception as e:
            if not no_error:
                logger.error(
                    f"TID: {self.task_id} | Element Activity | Description: {descriptor} | Error: {e}"
                )
            return False

    def _click_button(self, descriptor: str, xlocator: str, timeout: float = 0.2):
        """Clicks a button located by the specified locator."""
        try:
            button = self._check_element(
                descriptor=descriptor, xlocator=xlocator, timeout=timeout
            )
            self.driver.execute_script(
                """
                const button = arguments[0];
                if (button){
                    if (button.scrollIntoViewIfNeeded){
                        button.scrollIntoViewIfNeeded();
                    }
                    if (button.scrollIntoView){
                        button.scrollIntoView(true);
                    }
                    button.disabled = false; 
                    if (button.click){
                        button.click();
                    }
                }
                """,
                button,
            )
            self.driver.implicitly_wait(1)
            return True
        except Exception as e:
            logger.error(
                f"TID: {self.task_id} | Button Activity | Description: {descriptor} | Error: {e}"
            )
            return False

    def _enter_input_text(self, descriptor, xlocator: str, value: str | int):
        try:
            element = self._check_element(descriptor=descriptor, xlocator=xlocator)
            self.driver.execute_script(
                """
                const element = arguments[0];
                if (element){
                    if (element.scrollIntoView){
                        element.scrollIntoView(true);
                    }
                    if (element.focus){
                        element.focus()
                    }
                    element.value = ''
                    element.dispatchEvent(new Event('input'));  // Trigger 'input' event
                    element.value = arguments[1];  // Set the input value
                    element.dispatchEvent(new Event('input'));  // Trigger 'input' event
                    element.dispatchEvent(new Event('change'));  // Trigger 'change' event
                    if (element.blur){
                        element.blur()
                    }
                }
                """,
                element,
                value,
            )
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(
                f"TID: {self.task_id} | Input Activity | Description: {descriptor} | Error: {e}"
            )
            return False

    def _select(
        self,
        parent_descriptor,
        parent_label: str,
        option_descriptor,
        option_label: str,
    ):
        try:
            parent_xlocator = f"//div[text()='{parent_label.lower()}' or text()='{parent_label}']/ancestor::ng-select"
            select_parent_element = self._check_element(
                descriptor=parent_descriptor, xlocator=parent_xlocator, timeout=8
            )
            self.driver.execute_script(
                """
                    let select = arguments[0];
                    // Create the event, specifying the key you want to simulate
                    const event = new KeyboardEvent("keydown", {
                        key: 'Enter',      // Key you want to simulate
                        code: 'Enter',     // Code corresponding to the key
                        keyCode: 13,       // Key code for 'Enter' (13)
                        charCode: 13,
                        which: 13,
                        bubbles: true      // Allows the event to bubble up the DOM
                    });
                    if(select) {
                        select.dispatchEvent(event)
                    }
                """,
                select_parent_element,
            )
            if self._check_element(
                descriptor=f"{parent_descriptor} Dropdown Panel",
                xlocator=f"{parent_xlocator}//ng-dropdown-panel//div[contains(@class, 'ng-option')]",
                timeout=60,
            ):
                self.driver.implicitly_wait(2)
                button_xlocator = f"{parent_xlocator}//ng-dropdown-panel//div[contains(@class, 'ng-option')][.//span[text()='{option_label.lower()}' or text()='{option_label}']]"
                if self._check_element(
                    descriptor=option_descriptor,
                    xlocator=button_xlocator,
                    timeout=5,
                    no_error=True,
                ):
                    return self._click_button(
                        descriptor=option_descriptor,
                        xlocator=button_xlocator,
                        timeout=40,
                    )
                else:
                    return self._click_button(
                        descriptor=option_descriptor,
                        xlocator=f"{parent_xlocator}//ng-dropdown-panel//div[contains(@class, 'ng-option')][1]",
                        timeout=40,
                    )
            return False
        except Exception as e:
            logger.error(
                f"TID: {self.task_id} | Select Activity | Description: {parent_descriptor} and Option {option_descriptor} | Error: {e}"
            )
            self.teardown()
            return False

    def _select_input(self, parent_descriptor, parent_label: str, input_value: str):
        try:
            parent_xlocator = f"//div[text()='{parent_label.lower()}' or text()='{parent_label}']/ancestor::ng-select"
            select_parent_element = self._check_element(
                descriptor=parent_descriptor, xlocator=parent_xlocator, timeout=9
            )
            # Trigger Keydown event
            self.driver.execute_script(
                """
                    let select = arguments[0];
                    // Create the event, specifying the key you want to simulate
                    const event = new KeyboardEvent("keydown", {
                        key: 'Enter',      // Key you want to simulate
                        code: 'Enter',     // Code corresponding to the key
                        keyCode: 13,       // Key code for 'Enter' (13)
                        charCode: 13,
                        which: 13,
                        bubbles: true      // Allows the event to bubble up the DOM
                    });
                    if(select) {
                        select.dispatchEvent(event)
                    }
                """,
                select_parent_element,
            )
            # Input Element
            input_xlocator = f"{parent_xlocator}//input"
            input_element = self._check_element(
                descriptor=f"{parent_descriptor} Input Element",
                xlocator=input_xlocator,
                timeout="10",
            )
            if input_element:
                # Simulate typing each character in value with JavaScript `dispatchEvent`
                input_value = input_value.lower()
                # if "via" in input_value and len(input_value.split()) >= 2:
                #     input_value = " ".join(input_value.split()[:2])
                # input_value = input_value[:12]
                for char in input_value:
                    self.driver.execute_script(
                        """
                            let inputElement = arguments[0];
                            let char = arguments[1];

                            // Set the value of the input element
                            inputElement.value += char;

                            // Dispatch an 'input' event to simulate typing
                            const event = new Event('input', { bubbles: true });
                            inputElement.dispatchEvent(event);
                        """,
                        input_element,
                        char,
                    )
                    # Wait briefly between each character to simulate natural typing
                    time.sleep(0.3)
                time.sleep(1)
                # Optionally Selecting Suggestion
                if self._check_element(
                    descriptor=f"{parent_descriptor} Dropdown Panel",
                    xlocator=f"{parent_xlocator}//ng-dropdown-panel//div[contains(@class, 'ng-option')]",
                    timeout=60,
                ):
                    # If there is no element labelled not found, then continue
                    self.driver.implicitly_wait(2)
                    main_button_xlocator = f"""{parent_xlocator}//ng-dropdown-panel//div[contains(@class, 'ng-option')][.//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "{input_value}")]]"""
                    if self._check_element(
                        descriptor=f"Button {input_value}",
                        xlocator=main_button_xlocator,
                        timeout=5,
                        no_error=True,
                    ):
                        return self._click_button(
                            descriptor=f"{parent_descriptor} Dropdown Items of {input_value}",
                            xlocator=main_button_xlocator,
                            timeout=40,
                        )
                    else:
                        return self._click_button(
                            descriptor=f"Any first option of {parent_xlocator}",
                            xlocator=f"""{parent_xlocator}//ng-dropdown-panel//div[contains(@class, 'ng-option')][1]""",
                            timeout=40,
                        )

            self.driver.implicitly_wait(2)
            return False
        except Exception as e:
            logger.error(
                f"TID: {self.task_id} | Select & Input & Click Activity | Description: {parent_descriptor} and Value {input_value} | Error: {e}"
            )
            self.teardown()
            return False

    def _select_guide_expert_checkbox(self):
        try:
            parent_xlocator = f"//div[contains(@class, 'header')][.//div[text()=' Guida Esperta ' or text()='Guida Esperta']]"
            self._click_button(
                descriptor="Expert Guide/Guida Esperta [CLICK]",
                xlocator=parent_xlocator,
                timeout=20,
            )

            self.driver.implicitly_wait(2)
            return self.driver.execute_script(
                """
                    let select = arguments[0]
                    select.click();
                    arguments[1].dispatchEvent(new Event('checkedChange'));
                    select.dispatchEvent(new Event('blur'));
                    select.dispatchEvent(new Event('change'));
                    select.dispatchEvent(new Event('ngModelChange'));
                """,
                self._check_element(
                    descriptor="Checkbox switcher",
                    xlocator=f"{parent_xlocator}/ancestor::div//ivass-switcher//input[contains(@type, 'checkbox')]",
                ),
                self._check_element(
                    descriptor="Checkbox Ivass switcher",
                    xlocator=f"{parent_xlocator}/ancestor::div//ivass-switcher",
                ),
            )
        except Exception as e:
            logger.error(
                f"TID: {self.task_id} | Select & CheckBox | Description: Guide Expert | Error: {e}"
            )
            self.teardown()
            return False

    def continue_button(self, parent_xlocator=""):
        self.driver.implicitly_wait(2)
        # Next Section
        self._click_button(
            descriptor="Continue/Prosegui [Button]",
            xlocator=f"{parent_xlocator}//button[.//span[text()=' Prosegui ' or text()='Prosegui']]",
        )
        # Error
        self.check_if_any_error()
        return True

    def check_if_any_error(self):
        ## Check if there is any pop error or redirection to eot
        try:

            def message_checker(message):
                raise ValueError(
                    json.dumps(
                        jsonable_encoder(
                            {
                                "message": message,
                            }
                        )
                    )
                )

            if self._check_element(
                descriptor="App dialog error",
                xlocator="//app-dialog-error",
                timeout=2,
                no_error=True,
            ):
                return message_checker(
                    "App dialog error due to preregistration already done, but not fatal."
                )
            if self._check_element(
                descriptor="App dialog error",
                xlocator="//app-dialog-check-address",
                timeout=2,
                no_error=True,
            ):
                return message_checker(
                    "App dialog address error due to improper parsing of address, very fatal."
                )
            if self._check_element(
                descriptor="Service Error Page",
                xlocator="//app-service-error-page//div[contains(text(), 'Pagina di Errore')]",
                timeout=2,
                no_error=True,
            ):
                return message_checker(
                    "Service error page due to invalid data submission, improper proxy configuration, very fatal"
                )
            return True
        except Exception as e:
            raise e

    def solve_captcha(self):
        # Retry captcha frame if any issues occur
        restart_count = 0
        max_retries = 5
        descriptor = "Solving Recaptcha [iFRAME]"
        xlocator = "//iframe[contains(@title, 'reCAPTCHA')]"

        def restart_captcha_frame():
            nonlocal restart_count
            restart_count += 1
            logger.info(
                f"TID: {self.task_id} | Reloading captcha frame... (Attempt {restart_count}/{max_retries})"
            )

            # Only reload if the retry count has not exceeded max retries
            if restart_count <= max_retries:
                self.driver.execute_script(
                    """
                    var iframe = document.evaluate(arguments[0], document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (iframe) { iframe.src = iframe.src; }
                    """,
                    xlocator,
                )
                self.driver.implicitly_wait(3)
                # Retry solving the captcha
                self.solve_captcha()
                asyncio.sleep(2)
            else:
                logger.warning(
                    f"TID: {self.task_id} | Maximum retries reached ({max_retries}). Moving to the next step."
                )

        # Inject `retrieveCallback` function globally at the beginning of the session
        self.driver.execute_script(
            """
            window.retrieveCallback = function(obj, visited = new Set()) {
                if (typeof obj === 'function') return obj;
                for (const key in obj) {
                    if (!visited.has(obj[key])) {
                        visited.add(obj[key]);
                        if (typeof obj[key] === 'object' || typeof obj[key] === 'function') {
                            const value = retrieveCallback(obj[key], visited);
                            if (value) {
                                return value;
                            }
                        }
                        visited.delete(obj[key]);
                    }
                }
            };
        """
        )

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
                self.driver.switch_to.default_content()
                self.driver.execute_script(settings.FIND_RECAPTCHA_SCRIPT)
                self.driver.implicitly_wait(2)
                recaptcha_data = self.driver.execute_script(
                    "return findRecaptchaClients();"
                )
                if (
                    recaptcha_data
                    and isinstance(recaptcha_data, list)
                    and len(recaptcha_data) > 0
                ):
                    captcha_info = recaptcha_data[0]
                    logger.success(f"TID: {self.task_id} | 4.5 Solving Captcha ...")
                    # Initialize 2Captcha solver and use sitekey
                    solver = TwoCaptcha(settings.APIKEY_2CAPTCHA)
                    result = solver.solve_captcha(
                        site_key=captcha_info["sitekey"],
                        page_url=captcha_info.get("pageurl", self.driver.current_url),
                    )
                    logger.success(
                        f"TID: {self.task_id} | 4.6 Captcha Solved Successfully | Data: {result}"
                    )
                    if not result:
                        # result is None, and can't continue
                        logger.error(
                            f"TID: {self.task_id} | 2Captcha | Unable to Solve Captcha | Please crosscheck"
                        )
                        restart_captcha_frame(restart=False)
                        return False
                    # When you want to inject the CAPTCHA token
                    self.driver.execute_script(
                        """
                            const callback = window.retrieveCallback(window.___grecaptcha_cfg.clients[0]);
                            if (typeof callback === 'function') {
                                callback(arguments[0]);
                            } else {
                                throw new Error('Callback function not found.');
                            }
                        """,
                        result,
                    )
                    return result
                else:
                    logger.warning(
                        f"TID: {self.task_id} | Failed to retrieve reCAPTCHA data. Retrying..."
                    )
                    restart_captcha_frame()
            else:
                logger.warning(
                    f"TID: {self.task_id} | reCAPTCHA checkbox not found. Retrying..."
                )
                restart_captcha_frame()

        except Exception as e:
            logger.error(
                f"TID: {self.task_id} | Captcha Activity | Description: {descriptor} | Error: {e}"
            )
            restart_captcha_frame()

    # Check proxy validity with requests
    def check_proxy(self):
        # only continue code, if proxy is et
        try:
            # Set up the proxy and timeout
            proxies = {"http": self.proxy, "https": self.proxy}
            if settings.USE_PROXY or not not self.proxy:
                response = requests.get(
                    "http://ip-api.com/json", proxies=proxies, timeout=5
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
                        "proxy": self.proxy,
                    }
                else:
                    # Proxy country is not italy
                    logger.error(f"TID: {self.task_id} | Proxy is in the wrong country")
                    return {
                        "status": False,
                        "message": f"Current Proxy is in wrong country. Current [{data.get('countryCode', '')}] instead of [IT]",
                    }
            else:
                logger.error(
                    f"TID: {self.task_id} | Proxy check failed: status code is not status.HTTP_200_OK"
                )
                return {
                    "status": False,
                    "message": "Proxy request failed. Please try again",
                }
        except (RequestException, Timeout, Exception) as e:
            logger.error(f"TID: {self.task_id} | Proxy check failed {e}")
            return {
                "status": False,
                "message": "Proxy usage failed, Please try another.",
            }

    def parse_format_address(self):
        try:
            address = f"{self.anag.residenzaCivico}, {self.anag.residenzaIndirizzoVia} {self.anag.residenzaIndirizzo}, {self.anag.residenzaComune}, {self.anag.residenzaProvincia}"
            url = f"https://geocode.search.hereapi.com/v1/geocode?q={address}&apiKey={settings.HERE_API_KEY}"
            response = requests.get(url).json()

            if "items" in response and response["items"]:
                data = response["items"][0]["address"]
                street = data["street"]
                parts = street.split(maxsplit=1)
                via = parts[0]  # First part is "via"
                street_name = (
                    parts[1] if len(parts) > 1 else ""
                )  # The rest is the street name
                # Dictionary of common typos and corrections
                typo_corrections = {
                    "domencio": "domenico",
                    "pietrarsa": "pietrarse",
                    "fosso grande": "fossogrande",
                    # Add more common typos as needed
                }

                # Replace known typos in the street
                for typo, correction in typo_corrections.items():
                    street_name = street_name.lower().replace(typo, correction)
                self.anag.residenzaProvincia = data["countyCode"]
                self.anag.residenzaComune = data["city"]
                self.anag.residenzaIndirizzoVia = via
                self.anag.residenzaIndirizzo = street_name
                self.anag.residenzaCivico = data["houseNumber"]
                logger.success(
                    f"TID: {self.task_id} | 4.1 Corrected Address Metainfo successfully",
                )
            return True
        except Exception as e:
            logger.error(f"TID: {self.task_id} | Error | HERE Geocoder | {e}")
            return True

    def start(self):
        try:
            logger.success(f"TID: {self.task_id} | 4.0 Process | Starting Driver")
            # check proxy validity
            proxy_instance = self.check_proxy()
            if proxy_instance.get("status", False) and self.parse_format_address():
                # self.driver = webdriver.Remote(
                #     command_executor="http://localhost:4444/wd/hub",
                #     options=self.chrome_options(
                #         proxy=proxy_instance.get("proxy", None)
                #     ),
                # )
                self.driver = webdriver.Chrome(
                    options=self.chrome_options(proxy=proxy_instance.get("proxy", None))
                )
                self.wait = WebDriverWait(self.driver, timeout=10)
                if not self._reload_page_with_retry():
                    logger.error(
                        f"TID: {self.task_id} | Page Activity | Unable to load page, closing driver."
                    )
                    return self.teardown()
                idChoice = self.datiPreventivo.idScelta
                # CLICK [Consent]
                self._click_button(
                    descriptor="Consent/Acconsento [Button]",
                    xlocator="//button[.//span[text()=' Acconsento ']]",
                    timeout=60,
                )
                # CLICK [Vehicle Type]
                self._click_button(
                    descriptor=f"Select Vehicle Icon/{self.veicolo.tipoVeicolo} [IconButton]",
                    xlocator=f"//app-vehicle-picker//mat-button-toggle//button[contains(@aria-label, '{self.veicolo.tipoVeicolo.lower()}') or contains(@aria-label, '{self.veicolo.tipoVeicolo}')]",
                    timeout=20,
                )
                if str(idChoice) == "2" or int(idChoice) == 2:
                    return self.use_case_bersani()
                elif str(idChoice) == "1" or int(idChoice) == 1:
                    return self.use_case_classe_14()
                elif str(idChoice) == "3" or int(idChoice) == 3:
                    return self.use_case_recupero_attestato()
                elif str(idChoice) == "0" or int(idChoice) == 0:
                    # Valid for Autovettura, Motociclo, and Ciclomotore
                    return self.use_case_normale()
            else:
                self.teardown()
                return error_response_model(
                    {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "status": 5,
                        "message": proxy_instance.get(
                            "message",
                            "Error with proxy in processing request. Please try again later",
                        ),
                        "DataInizio": self.start_time.strftime("%d/%m/%Y %H:%M:%S"),
                        "DataFine": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "IdRicerca": self.datiPreventivo.idRicerca,
                        "Provenienza_IdValore": 999969,
                        "data": {
                            "Quotes": jsonable_encoder([]),
                            "Assets": {
                                "Marca": "",
                                "Modello": "",
                                "Allestimento": "",
                                "Valore": "",
                                "Cilindrata": "",
                                "DataImmatricolazione": "",
                            },
                        },
                    }
                )
        except Exception as e:
            logger.error(
                f"TID: {self.task_id} | <<< A WebDriver instace error occurred: {e}; Traceback: {traceback.format_exc()}>>>"
            )
            self.teardown()
            return error_response_model(
                {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "status": 5,
                    "message": e,
                    "DataInizio": self.start_time.strftime("%d/%m/%Y %H:%M:%S"),
                    "DataFine": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "IdRicerca": self.datiPreventivo.idRicerca,
                    "Provenienza_IdValore": 999969,
                    "data": {
                        "Quotes": jsonable_encoder([]),
                        "Assets": {
                            "Marca": "",
                            "Modello": "",
                            "Allestimento": "",
                            "Valore": "",
                            "Cilindrata": "",
                            "DataImmatricolazione": "",
                        },
                    },
                    **(json.loads(str(e)) if e else None),
                }
            )

    def check_vehicle_cilindrata(self):
        typeOfVehicle = self.veicolo.tipoVeicolo.lower()
        logger.info(
            f"TID: {self.task_id} | Checking Vehicle Cilindrata | Type of Vehicle: {typeOfVehicle} | Cilindrata: {self.veicolo.cilindrata} "
        )
        if (typeOfVehicle == "motociclo" and int(self.veicolo.cilindrata) <= 50) or (
            typeOfVehicle == "ciclomotore" and int(self.veicolo.cilindrata) > 50
        ):
            # Check for the cilindrata value if not matching condition throw eoror
            raise ValueError(
                json.dumps(
                    jsonable_encoder(
                        {
                            "status": 5,
                            "message": (
                                "Cilindrata is not greater than 50"
                                if typeOfVehicle == "motociclo"
                                else "Cilindrata is not less than or not equal to 50 "
                            ),
                        }
                    )
                )
            )
        return True

    def use_case_bersani(self):
        logger.success(
            f"TID: {self.task_id} | 4.4 Activating useCase 'Bersani' for {self.veicolo.tipoVeicolo.lower()}"
        )
        if self.check_vehicle_cilindrata():
            vehicleType = self.veicolo.tipoVeicolo
            if (
                vehicleType.lower() == "motociclo"
                or vehicleType.lower() == "ciclomotore"
            ):
                ## only if vehicleType is motociclo or ciclomotore
                self.normale_step_1()
            else:
                self.bersani_step_1()
            self.bersani_step_2(familyBonusText="Bonus Famiglia")
            self.bersani_step_3()
            self.bersani_step_4()
            self.bersani_step_5()
            self.bersani_step_6()
            return self.final_step()
        pass

    def use_case_classe_14(self):
        logger.success(
            f"TID: {self.task_id} | 4.4 Activating useCase 'classe 14' for {self.veicolo.tipoVeicolo.lower()}"
        )
        if self.check_vehicle_cilindrata():
            vehicleType = self.veicolo.tipoVeicolo
            if (
                vehicleType.lower() == "motociclo"
                or vehicleType.lower() == "ciclomotore"
            ):
                ## only if vehicleType is motociclo or ciclomotore
                self.normale_step_1()
            else:
                self.bersani_step_1()
            self.bersani_step_2(familyBonusText="Prima assicurazione", classe_14=True)
            self.bersani_step_3()
            self.bersani_step_4()
            self.bersani_step_5()
            self.bersani_step_6()
            return self.final_step()
        pass

    def use_case_recupero_attestato(self):
        logger.success(
            f"TID: {self.task_id} | 4.4 Activating useCase 'Recupero Attestato' for {self.veicolo.tipoVeicolo.lower()}"
        )
        if self.check_vehicle_cilindrata():
            vehicleType = self.veicolo.tipoVeicolo
            if (
                vehicleType.lower() == "motociclo"
                or vehicleType.lower() == "ciclomotore"
            ):
                ## only if vehicleType is motociclo or ciclomotore
                self.normale_step_1()
            else:
                self.bersani_step_1()
            self.recupero_attestato_step_2(
                familyBonusText="Ho già un attestato su un altro veicolo"
            )
            self.bersani_step_3()
            self.bersani_step_4()
            self.bersani_step_5()
            self.bersani_step_6()
            return self.final_step()
        pass

    def use_case_normale(self):
        logger.success(
            f"TID: {self.task_id} | 4.4 Activating useCase 'Normale' for {self.veicolo.tipoVeicolo.lower()}"
        )
        if self.check_vehicle_cilindrata():
            self.normale_step_1()
            # self.bersani_step_2()
            self.bersani_step_3()
            self.bersani_step_4()
            self.bersani_step_5()
            self.bersani_step_6()
            return self.final_step()
        pass

    def bersani_step_1(self):
        print("Bersani Step 1...")
        # CLICK [New Policy]
        self._click_button(
            descriptor="New Policy/Nuova Polizza [BUTTON] ",
            xlocator="//label[.//span[text()='Nuova Polizza']]",
        )
        # Enter Tax ID Code
        self._enter_input_text(
            descriptor="Enter the year in which you obtained your driving license/Inserisci anno di conseguimento della patente [INPUT]",
            xlocator="//mat-label[text()='Codice Fiscale']/ancestor::mat-form-field//input",
            value=f"{self.anag.cf}",
        )
        # CLICK [I already have the license plate]
        if self._click_button(
            descriptor="I already have the license plate/Ho già la targa",
            xlocator="//label[.//input[contains(@value, 'true')]]",
        ):
            # Enter Plate
            self._enter_input_text(
                descriptor="Plate/Targa [INPUT]",
                xlocator="//mat-label[text()='Targa']/ancestor::mat-form-field//input",
                value=self.veicolo.targa,
            )

        # Solve Captcha
        self.solve_captcha()

        # Continue Button
        self.continue_button()
        self.check_if_any_error()

    def normale_step_1(self):
        # CLICK [Renew Policy]
        self._click_button(
            descriptor="Renew Policy/Rinnovo Polizza [BUTTON] ",
            xlocator="//label[.//span[text()='Rinnovo Polizza']]",
        )
        # Enter Tax ID Code
        self._enter_input_text(
            descriptor="Enter the year in which you obtained your driving license/Inserisci anno di conseguimento della patente [INPUT]",
            xlocator="//mat-label[text()='Codice Fiscale']/ancestor::mat-form-field//input",
            value=f"{self.anag.cf}",
        )
        # Enter Plate
        self._enter_input_text(
            descriptor="Plate/Targa [INPUT]",
            xlocator="//mat-label[text()='Targa']/ancestor::mat-form-field//input",
            value=self.veicolo.targa,
        )
        # Solve Captcha
        self.solve_captcha()
        # Continue Button
        self.continue_button()
        self.check_if_any_error()

    def bersani_step_2(self, familyBonusText, classe_14: bool = False):
        print("Bersani Step 2")
        # SELECT [Risk certificate] _constant_
        self._select(
            parent_descriptor="Risk certificate/Attestato di rischio [SELECT]",
            parent_label="Attestato di rischio",
            option_descriptor=f"{familyBonusText} [OPTION]",
            option_label=familyBonusText,
        )
        if not classe_14:
            # ONly run in other classes but not classe 14
            # Enter Bonus Famiglia Tax ID Code
            self._enter_input_text(
                descriptor="Tax ID Code/Codice Fiscale [INPUT]",
                xlocator="//mat-label[text()='Codice Fiscale']/ancestor::mat-form-field//input",
                value=self.portante.cf,
            )
            # Enter Bonus Famiglia License Plate
            self._enter_input_text(
                descriptor="Reference plate/Targa di riferimento",
                xlocator="//mat-label[text()='Targa di riferimento']/ancestor::mat-form-field//input",
                value=self.portante.targa,
            )

    def recupero_attestato_step_2(self, familyBonusText):
        print("Recupero Attestato Step 2")
        # SELECT [Risk certificate] _constant_
        self._select(
            parent_descriptor="Risk certificate/Attestato di rischio [SELECT]",
            parent_label="Attestato di rischio",
            option_descriptor=f"{familyBonusText} [OPTION]",
            option_label=familyBonusText,
        )
        # CLICK [Vehicle Type]
        self._click_button(
            descriptor=f"Select Vehicle Icon/{self.portante.tipoVeicolo} [IconButton]",
            xlocator=f"//app-vehicle-picker//mat-button-toggle//button[contains(@aria-label, '{self.portante.tipoVeicolo.lower()}') or contains(@aria-label, '{self.portante.tipoVeicolo}')]",
            timeout=10,
        )
        # Enter License Plate
        self._enter_input_text(
            descriptor="Plate/Targa",
            xlocator="//mat-label[text()='Targa']/ancestor::mat-form-field//input",
            value=self.portante.targa,
        )

    def bersani_step_3(self):
        print("Bersani Step 3")
        # SELECT [Power Supply] _constant_
        self._select(
            parent_descriptor="Additional Power Supply/Alimentazione aggiuntiva [SELECT]",
            parent_label="Alimentazione aggiuntiva",
            option_descriptor="None/Nessuna [OPTION]",
            option_label="Nessuna",
        )
        # SELECT [Main Use] _constant_
        self._select(
            parent_descriptor="Main Use/Utilizzo Principale [SELECT]",
            parent_label="Utilizzo principale",
            option_descriptor="Home-work commute/Tragitto Casa-Lavoro [OPTION]",
            option_label="Tragitto Casa-Lavoro",
        )
        # SELECT [Annual Mileage] _constant_
        self._select(
            parent_descriptor="Annual Mileage/Percorrenza annua [SELECT]",
            parent_label="Percorrenza annua",
            option_descriptor="1500 Km [OPTION]",
            option_label="15000 Km",
        )
        # Input [Year and Month of Purchase]
        self._enter_input_text(
            descriptor="Year and Month of Purchase/Annose e mese d acquisto [INPUT]",
            xlocator="//mat-label[text()='Anno e mese di acquisto']/ancestor::mat-form-field//input",
            value=datetime(
                int(self.veicolo.acquistoAnno),
                int(self.veicolo.acquistoMese),
                int(self.veicolo.acquistoGiorno),
            ).strftime("%a %b %d %Y"),
        )
        # SELECT [Setup]
        self._select(
            parent_descriptor="Setup/Allestimento [SELECT]",
            parent_label="Allestimento",
            option_descriptor=f"{self.veicolo.allestimento} [OPTION]",
            option_label=f"{self.veicolo.allestimento}",
        )
        # Input [Date of first registration]
        self._enter_input_text(
            descriptor="Date of first registration/Data di prima immatricolazione [INPUT]",
            xlocator="//mat-label[text()='Data di prima immatricolazione']/ancestor::mat-form-field//input",
            value=datetime(
                int(self.veicolo.immatricolazioneAnno),
                int(self.veicolo.immatricolazioneMese),
                int(self.veicolo.immatricolazioneGiorno),
            ).strftime("%a %b %d %Y"),
        )

    def bersani_step_4(self):
        print("Next to Step 4")
        # SELECT [Marital Status] _constant_
        self._select(
            parent_descriptor="Marital Status/Stato civile [SELECT]",
            parent_label="Stato civile",
            option_descriptor="Other/Altro [OPTION]",
            option_label="Altro",
        )
        # SELECT [Numbers of Cars in household] _constant_
        self._select(
            parent_descriptor="Numbers of cars in household/Numero di auto nel nucleo familiare [SELECT]",
            parent_label="Numero di auto nel nucleo familiare",
            option_descriptor="Other/Altro [OPTION]",
            option_label="2",
        )
        # INPUT [Date of birth]
        self._enter_input_text(
            descriptor="Date of birth/Data di nascita [INPUT]",
            xlocator="//mat-label[text()='Data di nascita']/ancestor::mat-form-field//input",
            value=datetime(
                int(self.anag.nascitaAnno),  # Year
                int(self.anag.nascitaMese),  # Month
                int(self.anag.nascitaGiorno),  # Day
            ).strftime("%a %b %d %Y"),
        )
        # SELECT [Educational Qualification] _constant_
        self._select(
            parent_descriptor="Educational qualification/Titolo di studio [SELECT]",
            parent_label="Titolo di studio",
            option_descriptor="Diploma [OPTION]",
            option_label="Diploma",
        )
        # SELECT [Profession] _constant_
        self._select(
            parent_descriptor="Profession/Professione [SELECT]",
            parent_label="Professione",
            option_descriptor="Employee/Middle Manager/Private Official-Impiegato/Quadro/Funzionario Privato [OPTION]",
            option_label="Impiegato/Quadro/Funzionario Privato",
        )
        # SELECT [Children] _constant_
        self._select(
            parent_descriptor="Children/Figli [SELECT]",
            parent_label="Figli",
            option_descriptor="Yes (Only under 18s)/Si (Solo minori di 18 anni) [OPTION]",
            option_label="Si (Solo minori di 18 anni)",
        )
        # SELECT [Youngest driver age] _constant_
        self._select(
            parent_descriptor="Youngest Driver Age/Età guidatore più giovane [SELECT]",
            parent_label="Età guidatore più giovane",
            option_descriptor="25+ [OPTION]",
            option_label="25+",
        )
        # CLICK [I have a driving license] _constant_
        self._click_button(
            descriptor="I have a driving license/Non sono in possesso della patente di guida [BUTTON]",
            xlocator="//label[.//span[text()='Sono in possesso della patente di guida']]",
        )
        # INPUT [Enter the year in which you obtained your driving license]
        self._enter_input_text(
            descriptor="Enter the year in which you obtained your driving license/Inserisci anno di conseguimento della patente [INPUT]",
            xlocator="//mat-label[text()='Inserisci anno di conseguimento della patente']/ancestor::mat-form-field//input",
            value=f"{self.anag.patenteAnno}",
        )
        # SELECT& INPUT& CLICK [Provinces] <correction>
        self._select_input(
            parent_descriptor="Provinces/Provincia [SELECT&INPUT&CLICK]",
            parent_label="Provincia",
            input_value=f"{self.anag.residenzaProvincia}",
        )
        # SELECT & INPUT & CLICK [Common]
        self._select_input(
            parent_descriptor="Common/Comune [SELECT&INPUT&CLICK]",
            parent_label="Comune",
            input_value=f"{self.anag.residenzaComune}",
        )
        # SELECT & INPUT & CLICK [Street/Square/Avenue/etc]
        self._select_input(
            parent_descriptor="Street/Square/Avenue/etc-Via/Piazza/Viale/etc [SELECT&INPUT&CLICK]",
            parent_label="Via/Piazza/Viale/etc",
            input_value=f"{self.anag.residenzaIndirizzoVia} {self.anag.residenzaIndirizzo}",
        )
        # SELECT & INPUT & CLICK [Civico]
        self._enter_input_text(
            descriptor="Civico-Civic [SELECT&INPUT&CLICK]",
            xlocator="//mat-label[text()='Civico']/ancestor::mat-form-field//input",
            value=f"{self.anag.residenzaCivico}",
        )

    def bersani_step_5(self):
        print("Bersani step 5")
        # INPUT [New policy effective date]
        # self._enter_input_text(
        #     descriptor="New policy effective date/Data decorrenza nuova polizza [INPUT]",
        #     xlocator="//mat-label[text()='Data decorrenza nuova polizza']/ancestor::mat-form-field//input",
        #     value=datetime.strptime(
        #         str(self.veicolo.dataDecorrenza), "%d/%m/%Y"  # Date
        #     ).strftime("%a %b %d %Y"),
        # )
        # Continue
        self.continue_button()
        self.check_if_any_error()

    def bersani_step_6(self):
        print("Bersani Step 6")
        # Grant Clause
        # CLICK [EXPERT GUIDE]
        # Click only if data individual is older than 26 years old
        today = datetime.today()
        nascita_date = datetime(
            int(self.anag.nascitaAnno),
            int(self.anag.nascitaMese),
            int(self.anag.nascitaGiorno),
        )
        self.age = (
            today.year
            - nascita_date.year
            - ((today.month, today.day) < (nascita_date.month, nascita_date.day))
        )
        if self.age > 26:
            self._select_guide_expert_checkbox()
        self.continue_button()
        pass

    def final_step(self):
        print("Final Step & Preparing Quote Data")
        quote_object = []
        try:
            # Insurance Quote: Summary of data entered [DIALOG]
            if self._check_element(
                descriptor="Dialog of Summary",
                xlocator="//mat-dialog-container//h2",
                timeout=15,
            ):
                # Close Dialog & Continue
                self.continue_button(parent_xlocator="//mat-dialog-container")
                self.check_if_any_error()

                # Waiting for 30 seconds
                logger.success(
                    f"TID: {self.task_id} | 4.7 Gathering and Preparing Data..."
                )
                # List of quotes that satisfy the user's choice
                main_container = "//ivass-card-preventivo//ivass-card-simple//div[contains(@class, 'ivass-card-simple')]"
                if self._check_element(
                    descriptor="List of quotes that satisfy the user's choice",
                    xlocator=main_container,
                    timeout=60,
                ):
                    quote_cards = self.driver.find_elements(By.XPATH, main_container)
                    for card in quote_cards:
                        title_element = card.find_element(
                            By.XPATH,
                            ".//div[contains(@class, 'title')][@role='heading']",
                        )
                        title_text = title_element.text.strip()
                        # Extract the latest price within each card
                        # 1. Check for a discounted price first using `fix-width-min` class for the final discounted price
                        try:
                            price_element = card.find_element(
                                By.XPATH,
                                ".//div[contains(@class, 'fix-width-min')]",
                            )
                            price_text = (
                                price_element.text.strip()
                            )  # Remove extra whitespace
                        except:
                            # 2. If no discounted price is found, fallback to the regular price using `price-container`
                            price_element = card.find_element(
                                By.XPATH,
                                ".//div[contains(@class, 'price-container')]",
                            )
                            price_text = price_element.text.strip()

                        # Clean up the price & guida text
                        price_text = re.sub(
                            r"Prezzo Scontato\s*", "", price_text
                        )  # Remove "Prezzo Scontato" and any following spaces/newlines
                        price_text = re.sub(
                            r"Prezzo ufficiale\s*", "", price_text
                        )  # Remove "Prezzo Scontato" and any following spaces/newlines
                        price_text = price_text.replace(".", "").replace(",", ".")
                        if self.age > 26:
                            guida_text = "Esperta"
                        else:
                            guida_text = "Libera"
                        price_text = price_text.replace(" €", "")
                        # Append extracted data to the list as a dictionary
                        quote_object.append(
                            {
                                "IdAccordo": self.datiPreventivo.idAccordo,
                                "IdFascia": self.datiPreventivo.idFascia,
                                "Sito": "preventivass.it",
                                "Compagnia": title_text,
                                "Prodotto": "RCA",
                                "Emissione": "",
                                "Massimale": "",
                                "Guida": guida_text,
                                "Include": "",
                                "Prezzo_Totale": price_text,
                                "Prezzo_Iniziale": "",
                                "Prezzo_RCA": price_text,
                                "Dettagli": "",
                                "StatoPreventivoAcquistabile": 1,
                                "IdPreventivo": "",
                                "NotePreventivo": "",
                                "Satellitare": 0,
                            }
                        )
            self.teardown()
            if quote_object:
                if len(quote_object) > 0:
                    return success_response_model(
                        {
                            "code": status.HTTP_200_OK,
                            "status": 1,
                            "message": "Data fetched successfully",
                            "DataInizio": self.start_time.strftime("%d/%m/%Y %H:%M:%S"),
                            "DataFine": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            "IdRicerca": self.datiPreventivo.idRicerca,
                            "Provenienza_IdValore": 999969,
                            "data": {
                                "Quotes": jsonable_encoder(quote_object),
                                "Assets": {
                                    "Marca": "",
                                    "Modello": "",
                                    "Allestimento": "",
                                    "Valore": "",
                                    "Cilindrata": "",
                                    "DataImmatricolazione": "",
                                },
                            },
                        }
                    )
            return error_response_model(
                {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "status": 5,
                    "message": "Issue with processing request, there was empty data. Please try again.",
                    "DataInizio": self.start_time.strftime("%d/%m/%Y %H:%M:%S"),
                    "DataFine": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "IdRicerca": self.datiPreventivo.idRicerca,
                    "Provenienza_IdValore": 999969,
                    "data": {
                        "Quotes": jsonable_encoder(quote_object),
                        "Assets": {
                            "Marca": "",
                            "Modello": "",
                            "Allestimento": "",
                            "Valore": "",
                            "Cilindrata": "",
                            "DataImmatricolazione": "",
                        },
                    },
                }
            )
        except Exception as e:
            logger.error(
                f"TID: {self.task_id} | <<< A WebDriver instace error occurred: {e}; Traceback: {traceback.format_exc()}>>>"
            )
            self.teardown()
            return error_response_model(
                {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "status": 5,
                    "message": e,
                    "DataInizio": self.start_time.strftime("%d/%m/%Y %H:%M:%S"),
                    "DataFine": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "IdRicerca": self.datiPreventivo.idRicerca,
                    "Provenienza_IdValore": 999969,
                    "data": {
                        "Quotes": jsonable_encoder(quote_object),
                        "Assets": {
                            "Marca": "",
                            "Modello": "",
                            "Allestimento": "",
                            "Valore": "",
                            "Cilindrata": "",
                            "DataImmatricolazione": "",
                        },
                    },
                    **(json.loads(str(e)) if e else None),
                }
            )
