## Reference
these are setup to setups of how the bots is up and working

## Creating virtual environment
```
python -m venv venv
```

## Activating the Virtual Environment
```
vass\Scripts\activate.bat
```

## Setup Environment Variable
Inside your .env file

|    Variable     |     Type      |              Default               | Description                                                                                                                                                     |
|:---------------:|:-------------:|:----------------------------------:| --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|    USE_PROXY    |     bool      |               False                | Makes selenium browser to map location to **Italy** as that is the default country for *preventivass.it* to work                                                |
|   PROXY_TYPE    |    string     |              "socks4"              | The socks protocol can be http, https, socks4, socks5, tor and others                                                                                           |
|     DB_HOST     |    string     |            "localhost"             | The database hostname or ip                                                                                                                                     |
|     DB_PORT     | string or int |                3306                | The database port                                                                                                                                               |
|   DB_DATABASE   |    string     |                 ""                 | The database name                                                                                                                                               |
|   DB_USERNAME   |    string     |                 ""                 | The database username                                                                                                                                           |
|   DB_PASSWORD   |    string     |                 ""                 | The database password                                                                                                                                           |
|  HERE_API_KEY   |    string     |                 ""                 | Use for geolocation encoding. Parsing the address for autocorrection with website                                                                               |
|  ALLOWED_HOSTS  |     list      |         ["localhost", "*"]         | The controls which hosts can access the API and its resources                                                                                                   |
|   USE_TG_BOT    |     bool      |               False                | Use telegram bots to receive bot logs. To start using, start the "@PreventivassBot" on Telegram and /start command, then contact developer to give you CHAT_ID. |
|     CHAT_ID     |    string     |                 ""                 | Telegram Chat ID for bots to send logs to                                                                                                                       |
| APIKEY_2CAPTCHA |    string     | "1f900baf6f486e66db38ba2a8efe5f0d" | 2Captcha Api Key                                                                                                                                                |



## Importing Models
```
from database import Base, engine
from utils.models import QuoteData
Base.metadata.create_all(bind=engine)
```

## Exporting Python Packages to Requirements
```
pip-chill > requirements.txt
```

## Package Python pkg in requirements.txt
```
pip install -r requirements.txt
```

## RUN APP
```
python main.py
```

## Curl Command To Check Proxy Status
```
curl --connect-timeout 5 --max-time 10 --retry 1 --retry-connrefused --location --request GET "http://ip-api.com/json" --proxy socks4://proxy_ip
```

# Important Documentations and References
[Working with html iframe in selenium](https://www.selenium.dev/documentation/webdriver/interactions/frames/)
[Working with xPath locator in selenium](https://www.browserstack.com/guide/xpath-in-selenium)