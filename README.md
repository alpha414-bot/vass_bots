[Reference:](https://github.com/DefiWimar/Major-TG-App-Bot)
these are setup to setups of how the bots is up and working

[create virtual environment of vass]()
```
python -m venv venv
```

[Activating the Virtual Environment ]()
```
vass\Scripts\activate.bat
```

[Importing Models]()
```
from database import Base, engine
from utils.models import QuoteData
Base.metadata.create_all(bind=engine)
```

[Exporting Python Packages to Requirements]()
```
pip freeze > requirements.txt
```

[Install Python Packagas in requirements.txt]()
```
pip install -r requirements.txt
```

[Curl Command To Check Proxy Status]()
```
curl --connect-timeout 5 --max-time 10 --retry 1 --retry-connrefused --location --request GET "http://ip-api.com/json" --proxy socks4://proxy_ip
```



# Important Documentations and References
[Working with html iframe in selenium](https://www.selenium.dev/documentation/webdriver/interactions/frames/)
[Working with xPath locator in selenium](https://www.browserstack.com/guide/xpath-in-selenium)