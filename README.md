#### Reference:
these are setup to setups of how the bots is up and working

#### Creating virtual environment for bot
```
python -m venv venv
```

#### Activating the Virtual Environment
```
vass\Scripts\activate.bat
```

#### Setup Environment Variable
Inside your .env file
| Variable                 | Type   | Default      | Description                                                                            |
| -------------------- | ------ | -------- | ------------ | -------------------------------------------------------------------------------------- |
| USE_PROXY         | bool | False            | Default Value that can be set based on OTP / Pin received from parent container.       |
| handleTextChange     | func   | No       | n/a          | callback with concated string of all cells as argument.                                |
| handleCellTextChange | func   | Yes      | n/a          | callback for text change in individual cell with cell text and cell index as arguments |
| inputCount           | number | Yes      | 4            | Number of Text Input Cells to be present.                                              |
| tintColor            | string | Yes      | #3CB371      | Color for Cell Border on being focused.                                                |
| offTintColor         | string | Yes      | #DCDCDC      | Color for Cell Border Border not focused.                                              |
| inputCellLength      | number | Yes      | 1            | Number of character that can be entered inside a single cell.                          |
| containerStyle       | object | Yes      | {}           | style for overall container.                                                           |
| textInputStyle       | object | Yes      | {}           | style for text input.                                                                  |
| testIDPrefix         | string | Yes      | 'otp*input*' | testID prefix, the result will be `otp_input_0` until inputCount                       |
| autoFocus            | bool   | Yes      | false        | Input should automatically get focus when the components loads                         |


#### Importing Models
```
from database import Base, engine
from utils.models import QuoteData
Base.metadata.create_all(bind=engine)
```

#### Exporting Python Packages to Requirements
```
pip freeze > requirements.txt
```

#### Package Python pkg in requirements.txt
```
pip install -r requirements.txt
```

#### Curl Command To Check Proxy Status
```
curl --connect-timeout 5 --max-time 10 --retry 1 --retry-connrefused --location --request GET "http://ip-api.com/json" --proxy socks4://proxy_ip
```



# Important Documentations and References
[Working with html iframe in selenium](https://www.selenium.dev/documentation/webdriver/interactions/frames/)
[Working with xPath locator in selenium](https://www.browserstack.com/guide/xpath-in-selenium)