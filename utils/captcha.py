import time
import requests


class TwoCaptcha(object):
    def __init__(self, api_key, sleep_time=2):
        self.api_key = api_key
        self.sleep_time = sleep_time

    def __get_captcha_id(self, site_key, page_url):
        params = {
            "googlekey": site_key,
            "pageurl": page_url,
            "method": "userrecaptcha",
            "key": self.api_key,
            "json": 1,
        }
        endpoint = "http://2captcha.com/in.php"
        response = requests.post(endpoint, params=params)
        print("please work text", response.text)
        print("please work json", response.json)
        print("please work json 2", response.json())
        response = response.json()
        if not response.get("status"):
            print("There was an error")
            return None
        captcha_id = response.get("request", "")
        return captcha_id

    def __get_captcha_token(self, captcha_id):
        params = {"ids": captcha_id, "action": "get", "key": self.api_key}
        endpoint = "http://2captcha.com/res.php"
        response = requests.get(endpoint, params=params)
        print("response text please remember to remove this line", response.text)
        while "CAPCHA_NOT_READY" in response.text:
            time.sleep(self.sleep_time)
            response = requests.get(endpoint, params=params)
        captcha_token = response.text
        return captcha_token

    def solve_captcha(self, site_key, page_url):
        try:
            captcha_id = self.__get_captcha_id(site_key, page_url)
            if not not captcha_id:
                captcha_token = self.__get_captcha_token(captcha_id)
                return captcha_token
            return None
        except:
            return None

    def get_balance(self):
        params = {"action": "getbalance", "json": 1, "key": self.api_key}
        endpoint = "http://2captcha.com/res.php"
        response = requests.get(endpoint, params=params)
        response_json = response.json()

        balance = None
        if response_json.get("status", 0) == 1:
            balance = response_json.get("request", None)

        if balance:
            return balance
        else:
            raise ValueError("2Captcha returned invalid balance")
