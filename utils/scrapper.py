import asyncio
import json
import re
import time
import traceback
import datetime
from fastapi import status
from fastapi.encoders import jsonable_encoder
from logger import logger
from fake_useragent import UserAgent
from response import error_response_model, success_response_model
from utils.models import QuoteData
from utils.schemas import RawRequestData
from utils.settings import settings
from .captcha import TwoCaptcha
from sqlalchemy.orm import Session
import requests
from requests.exceptions import RequestException, Timeout
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException


class Scrapper:
    def __init__(self, data: RawRequestData, db: Session):
        logger.success("0.0 Process | Initiating Scrapper Class On Selenium")
        self.db = db
        proxy = data.proxy
        captcha_token = data.captcha_token
        self.req = data
        self.proxy = None
        self.captcha_token = None
        if proxy:
            self.proxy = f"socks4://{proxy}"
        if captcha_token:
            self.captcha_token = captcha_token
        self.running = True
        self.captcha_retry_attempts = 3
        self.retry_attempts = 3  # Max retry Attempts

    def chrome_options(self):
        options = Options()
        options.add_experimental_option("detach", True)
        # chrome_options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--user-agent={UserAgent(os='windows').random}")
        # options.add_argument("--disable-gpu")  # Applicable on Windows
        if self.proxy:
            options.add_argument(f"--proxy-server={self.proxy}")
        return options

    def teardown(self):
        """Teardown method to quit the WebDriver and show a message box."""
        logger.success(f"Terminating Session")
        self.driver.quit()
        return error_response_model(
            {
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Issue with processing request. Please try again.",
            }
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
                logger.success(f"1.1 Attempt {attempt} to load the page.")
                self.driver.get("https://www.preventivass.it/dati-principali")

                if self._is_page_loaded():
                    logger.success("1.2 Page loaded successfully.")
                    return True
                else:
                    raise TimeoutException("Page not loaded within timeout.")
            except (TimeoutException, WebDriverException, Exception) as e:
                logger.warning(
                    f"Load attempt {attempt} failed: {e} traceback: {traceback.format_exc()}"
                )
                if attempt < self.retry_attempts:
                    asyncio.sleep(2)  # Wait before retrying
                else:
                    logger.warning("Failed to load the page after multiple attempts.")
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
        except:
            if not no_error:
                logger.error(
                    f"Element Activity | Description: {descriptor} | Error: {traceback.format_exc()}"
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
                button.scrollIntoViewIfNeeded();
                button.scrollIntoView(true);
                button.disabled = false; 
                button.click();
                """,
                button,
            )
            self.driver.implicitly_wait(1)
            return True
        except:
            logger.error(
                f"Button Activity | Description: {descriptor} | Error: {traceback.format_exc()}"
            )
            return False

    def _enter_input_text(self, descriptor, xlocator: str, value: str | int):
        try:
            element = self._check_element(descriptor=descriptor, xlocator=xlocator)
            self.driver.execute_script(
                """
                const element = arguments[0];
                element.scrollIntoView(true);
                element.focus()
                element.value = ''
                element.dispatchEvent(new Event('input'));  // Trigger 'input' event
                element.value = arguments[1];  // Set the input value
                element.dispatchEvent(new Event('input'));  // Trigger 'input' event
                element.dispatchEvent(new Event('change'));  // Trigger 'change' event
                element.blur()
                """,
                element,
                value,
            )
            time.sleep(1)
            return True
        except:
            logger.error(
                f"Input Activity | Description: {descriptor} | Error: {traceback.format_exc()}"
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
                xlocator=f"{parent_xlocator}//ng-dropdown-panel",
                timeout=15,
            ):
                return self._click_button(
                    descriptor=option_descriptor,
                    xlocator=f"{parent_xlocator}//ng-dropdown-panel//div[contains(@class, 'ng-option')][.//span[text()='{option_label.lower()}' or text()='{option_label}']]",
                    timeout=10,
                )
            return False
        except:
            logger.error(
                f"Select Activity | Description: {parent_descriptor} and Option {option_descriptor} | Error: {traceback.format_exc()}"
            )
            return False

    def _select_input(self, parent_descriptor, parent_label: str, input_value: str):
        try:
            parent_xlocator = f"//div[text()='{parent_label.lower()}' or text()='{parent_label}']/ancestor::ng-select"
            select_parent_element = self._check_element(
                descriptor=parent_descriptor, xlocator=parent_xlocator, timeout=8
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
                descriptor=f"{parent_descriptor} Input Element", xlocator=input_xlocator
            )
            if input_element:
                # Simulate typing each character in value with JavaScript `dispatchEvent`
                input_value = input_value.lower()
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
                    time.sleep(0.2)
                self.driver.implicitly_wait(2)
                # Optionally Selecting Suggestion
                if self._check_element(
                    descriptor=f"{parent_descriptor} Dropdown Panel",
                    xlocator=f"{parent_xlocator}//ng-dropdown-panel",
                    timeout=40,
                ):
                    # If there is no element labelled not found, then continue
                    self.driver.implicitly_wait(2)
                    return self._click_button(
                        descriptor=f"{parent_descriptor} Dropdown Items of {input_value}",
                        xlocator=f"""{parent_xlocator}//ng-dropdown-panel//div[contains(@class, 'ng-option')][.//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "{input_value}")]]""",
                        timeout=15,
                    )

            self.driver.implicitly_wait(2)
            return True
        except:
            logger.error(
                f"Select & Input & Click Activity | Description: {parent_descriptor} and Value {input_value} | Error: {traceback.format_exc()}"
            )
            return False

    def _select_guide_expert_checkbox(self):
        try:
            parent_xlocator = (
                f"//div[contains(@class, 'header')][.//div[text()=' Guida Esperta ']]"
            )
            self._click_button(
                descriptor="Expert Guide/Guida Esperta [CLICK]",
                xlocator=parent_xlocator,
                timeout=15,
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
        except:
            logger.error(
                f"Select & CheckBox | Description: Guide Expert | Error: {traceback.format_exc()}"
            )
            return False

    def solve_captcha(self, descriptor, xlocator):
        # Retry captcha frame if any issues occur
        restart_count = 0
        max_retries = 5

        def restart_captcha_frame():
            nonlocal restart_count
            restart_count += 1
            logger.info(
                f"Reloading captcha frame... (Attempt {restart_count}/{max_retries})"
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
                self.solve_captcha(
                    descriptor=descriptor,
                    xlocator=xlocator,
                    restart_count=restart_count,
                )
                asyncio.sleep(2)
            else:
                logger.warning(
                    f"Maximum retries reached ({max_retries}). Moving to the next step."
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
                    logger.info(f"reCAPTCHA info found: {captcha_info}")

                    # Solve Captcha
                    if self.captcha_token:
                        # captcha is solved and sent with request
                        logger.success(
                            f"Captcha Token from request: {self.captcha_token}"
                        )
                        self.driver.execute_script(
                            """
                                const callback = window.retrieveCallback(window.___grecaptcha_cfg.clients[0]);
                                if (typeof callback === 'function') {
                                    callback(arguments[0]);
                                } else {
                                    throw new Error('Callback function not found.');
                                }
                            """,
                            self.captcha_token,
                        )
                    else:
                        # Initialize 2Captcha solver and use sitekey
                        solver = TwoCaptcha(settings.APIKEY_2CAPTCHA)
                        result = solver.solve_captcha(
                            site_key=captcha_info["sitekey"],
                            page_url=captcha_info.get(
                                "pageurl", self.driver.current_url
                            ),
                        )
                        if not result:
                            # result is None, and can't continue
                            logger.error(
                                "2Captcha | Unable to Solve Captcha | Please crosscheck"
                            )
                            restart_captcha_frame(restart=False)
                            return False
                        logger.success(f"Solved captcha: {result}")
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
                    if data.get("countryCode", "").lower() == "it":
                        # Check if proxy country is pointed to "Italy"
                        return True
                    else:
                        # Proxy country is not italy
                        return False
                else:
                    logger.error(
                        f"Proxy check failed: status code is not status.HTTP_200_OK"
                    )
                    return False
            except (RequestException, Timeout, Exception) as e:
                logger.error(
                    f"Proxy check failed {e} | Traceback: {traceback.format_exc()}"
                )
                return False
        else:
            # return True, if there is no proxy with request
            return True

    def insert_into_db(self, response):
        try:
            # Insertin into database
            data = self.req.data
            new_quote_data = QuoteData(
                request_data={
                    "anag": {
                        "cf": data.anag.cf,
                        "nascitaGiorno": data.anag.nascitaGiorno,
                        "nascitaMese": data.anag.nascitaMese,
                        "nascitaAnno": data.anag.nascitaAnno,
                        "patenteAnno": data.anag.patenteAnno,
                        "residenzaProvincia": data.anag.residenzaProvincia,
                        "residenzaComune": data.anag.residenzaComune,
                        "residenzaIndirizzoVia": data.anag.residenzaIndirizzoVia,
                        "residenzaIndirizzo": data.anag.residenzaIndirizzo,
                        "residenzaCivico": data.anag.residenzaCivico,
                    },
                    "veicolo": {
                        "targa": data.veicolo.targa,
                        "acquistoGiorno": data.veicolo.acquistoGiorno,
                        "acquistoMese": data.veicolo.acquistoMese,
                        "acquistoAnno": data.veicolo.acquistoAnno,
                        "allestimento": data.veicolo.allestimento,
                        "immatricolazioneGiorno": data.veicolo.immatricolazioneGiorno,
                        "immatricolazioneMese": data.veicolo.immatricolazioneMese,
                        "immatricolazioneAnno": data.veicolo.immatricolazioneAnno,
                        "dataDecorrenza": data.veicolo.dataDecorrenza,
                    },
                },
                response_data=json.dumps(jsonable_encoder(response)),
            )
            self.db.add(new_quote_data)
            self.db.commit()
            self.db.refresh(new_quote_data)
            return new_quote_data
        except:
            logger.error(f"There was a problem inserting {response} to database")
            return False

    def start(self):
        logger.success("1.0 Process | Starting Driver")
        # check proxy validity
        if self.check_proxy():
            self.driver = webdriver.Chrome(options=self.chrome_options())
            self.wait = WebDriverWait(self.driver, timeout=10)
            if not self._reload_page_with_retry():
                logger.error("Page Activity | Unable to load page, closing driver.")
                return self.teardown()

            data = self.req.data
            quote_object = []
            # CLICK [Consent]
            self._click_button(
                descriptor="Consent/Acconsento [Button]",
                xlocator="//button[.//span[text()=' Acconsento ']]",
                timeout=60,
            )

            # CLICk [Vehicle] _constant_
            self._click_button(
                descriptor="Select Vehicle Icon/Autovettura [IconButton]",
                xlocator="//button[@id='mat-button-toggle-3-button']",
                timeout=20,
            )
            # CLICK [Renew Policy] _cnstant_
            self._click_button(
                descriptor="Renew Policy/Rinnovo Polizza [BUTTON] ",
                xlocator="//label[.//span[text()='Rinnovo Polizza']]",
            )

            # Enter Tax ID Code and Plate
            self._enter_input_text(
                descriptor="Tax ID Code/Codice Fiscale [INPUT]",
                xlocator="//input[@id='mat-input-0']",
                value=data.anag.cf,
            )
            self._enter_input_text(
                descriptor="Plate/Targa [INPUT]",
                xlocator="//input[@id='mat-input-1']",
                value=data.veicolo.targa,
            )

            # Solve Captcha
            self.solve_captcha(
                descriptor="Solving Recaptcha [iFRAME]",
                xlocator="//iframe[contains(@title, 'reCAPTCHA')]",
            )

            # Continue Button Next Section
            self._click_button(
                descriptor="Continue/Prosegui [Button]",
                xlocator="//button[.//span[text()='Prosegui']]",
            )
            self.driver.implicitly_wait(2)
            # Service Page Issue
            if self._check_element(
                descriptor="Service Error Page",
                xlocator="//app-service-error-page//div[contains(text(), 'Pagina di Errore')]",
                no_error=True,
            ):
                return self.teardown()
            self.driver.implicitly_wait(1)
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
                value=f"{data.veicolo.acquistoGiorno}/{data.veicolo.acquistoMese}/{data.veicolo.acquistoAnno}",  # d-m-y
            )
            # SELECT [Setup]
            self._select(
                parent_descriptor="Setup/Allestimento [SELECT]",
                parent_label="Allestimento",
                option_descriptor=f"{data.veicolo.allestimento} [OPTION]",
                option_label=f"{data.veicolo.allestimento}",
            )
            # Input [Date of first registration]
            self._enter_input_text(
                descriptor="Date of first registration/Data di prima immatricolazione [INPUT]",
                xlocator="//mat-label[text()='Data di prima immatricolazione']/ancestor::mat-form-field//input",
                value=datetime.date(
                    int(data.veicolo.immatricolazioneAnno),
                    int(data.veicolo.immatricolazioneMese),
                    int(data.veicolo.immatricolazioneGiorno),
                ).strftime("%m/%d/%Y"),
            )

            # MAJOR CONSTANTS VALUES
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
                value=datetime.date(
                    int(data.anag.nascitaAnno),  # Year
                    int(data.anag.nascitaMese),  # Month
                    int(data.anag.nascitaGiorno),  # Day
                ).strftime("%m/%d/%Y"),
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
                value=f"{data.anag.patenteAnno}",
            )
            # SELECT& INPUT& CLICK [Provinces]
            self._select_input(
                parent_descriptor="Provinces/Provincia [SELECT&INPUT&CLICK]",
                parent_label="Provincia",
                input_value=f"{data.anag.residenzaProvincia}",
            )
            # SELECT & INPUT & CLICK [Common]
            self._select_input(
                parent_descriptor="Common/Comune [SELECT&INPUT&CLICK]",
                parent_label="Comune",
                input_value=f"{data.anag.residenzaComune}",
            )
            # SELECT & INPUT & CLICK [Street/Square/Avenue/etc]
            self._select_input(
                parent_descriptor="Street/Square/Avenue/etc-Via/Piazza/Viale/etc [SELECT&INPUT&CLICK]",
                parent_label="Via/Piazza/Viale/etc",
                input_value=f"{data.anag.residenzaIndirizzoVia} {data.anag.residenzaIndirizzo}",
            )
            # SELECT & INPUT & CLICK [Civico]
            self._enter_input_text(
                descriptor="Civico-Civic [SELECT&INPUT&CLICK]",
                xlocator="//mat-label[text()='Civico']/ancestor::mat-form-field//input",
                value=f"{data.anag.residenzaCivico}",
            )
            # INPUT [New policy effective date]
            self._enter_input_text(
                descriptor=f"New policy effective date/Data decorrenza nuova polizza [INPUT]",
                xlocator="//mat-label[text()='Data decorrenza nuova polizza']/ancestor::mat-form-field//input",
                value=datetime.datetime.strptime(
                    data.veicolo.dataDecorrenza, "%d/%m/%Y"
                ).strftime("%m/%d/%Y"),
            )
            self.driver.implicitly_wait(2)
            # Next Section
            self._click_button(
                descriptor="Continue/Prosegui [Button]",
                xlocator="//button[.//span[text()=' Prosegui ']]",
            )

            self.driver.implicitly_wait(2)
            # Service Page Issue
            if self._check_element(
                descriptor="Service Error Page",
                xlocator="//app-service-error-page//div[contains(text(), 'Pagina di Errore')]",
                no_error=False,
            ):
                return self.teardown()
            # Grant Clause
            # CLICK [EXPERT GUIDE]
            self._select_guide_expert_checkbox()
            # Next Section
            self._click_button(
                descriptor="Continue/Prosegui [Button]",
                xlocator="//button[.//span[text()=' Prosegui ']]",
            )
            # Insurance Quote: Summary of data entered [DIALOG]
            if self._check_element(
                descriptor="Dialog of Summary",
                xlocator="//mat-dialog-container//h2",
                timeout=15,
            ):
                # Next Section
                self._click_button(
                    descriptor="Continue/Prosegui [Button]",
                    xlocator="//mat-dialog-container//button[.//span[text()=' Prosegui ']]",
                )

                # Waiting for 30 seconds
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
                        title_text = title_element.text

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
                            # price_element = card.find_element(
                            #     By.XPATH, ".//div[@class='price-container']"
                            # )
                            price_element = card.find_element(
                                By.XPATH,
                                ".//div[contains(@class, 'price-container')]",
                            )
                            price_text = price_element.text.strip()

                        # Clean up the price text
                        price_text = re.sub(
                            r"Prezzo Scontato\s*", "", price_text
                        )  # Remove "Prezzo Scontato" and any following spaces/newlines
                        # price_text = price_text.replace(" €", "")
                        # Append extracted data to the list as a dictionary
                        quote_object.append({"title": title_text, "price": price_text})

            db_quote_data = self.insert_into_db(response=quote_object)
            self.teardown()
            if db_quote_data:
                return success_response_model(
                    {
                        "code": status.HTTP_200_OK,
                        "request_id": db_quote_data.id,
                        "data": jsonable_encoder(quote_object),
                    }
                )
            else:
                return error_response_model(
                    {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "Issue with processing request. Please try again.",
                    }
                )
        else:
            return error_response_model(
                {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Proxy is invalid. Try another.",
                }
            )


BotScrapper = Scrapper
