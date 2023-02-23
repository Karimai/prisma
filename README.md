The FastAPI framework is used for this code challenge project.

### Docker
Two services (containers) are created:
* prisma_task: An image is build by the Dockerfile. It is the main app.
* prisma_task_logs: It is considered for logs. The main purpose is how we can dedicate a container for logs. The reference image is `busybox`. A volume is being used to save logs.

run the bellow command to build the project and run it.
`doccker-compse up --build`

### Code Styling
Three tools are being used in this project caring for code convention; isort, black, and flake8. Please run every tools before trying to commit the code:
* isort .
* black .
* flake .

### Security
There are two security APIKEY for fetching data from third-parties. All are kept in the .env and later loaded by dotenv package.
(For the sake of simplicity, I will put this file into the repository, it should not be indeed. It should be user (developer here) responsibility to give them proper values)

### Algorithm:
The stocks api receives a json which include three parameters:
symbol, currency, and date_range.

There is no validation check for symbol. It is enough to be a string.
currency is checked by currencies package. The currency should be a valid currency such as EUR or USD. A String like `KARIM` is no valid.
data_range should be in the format of mentioned in the Code Challenge description.

First api call will be to [Exchangerates](https://api.apilayer.com/exchangerates_data/timeseries). It mainly returns the rates of an exchange between two currencies such as `USD` to `EUR`.

The second third-part API call will to the [Marketstack](http://api.marketstack.com/v1/eod). The `close` property will be used for an input ticker.
In case, there is no return value for a ticker in a date, the close rate of previous day will be used. In case, it is the first day, the rate of `1.0` is considered.

The return includes symbol, currency, and daily_close. A sample response is presented here:
Response body
{
  "symbol": "AAPL",
  "currency": "EUR",
  "daily_close": {
    "2022-10-10": 144.6,
    "2022-10-11": 143.3,
    "2022-10-12": 142.5,
    "2022-10-13": 146.7,
    "2022-10-23": 142.4,
    "2022-10-24": 151.2,
    "2022-10-25": 152.9
    }
}

### test
two simple tests are present in the test_main.html and test_main.py.


### pre-commit
Please install pre-commit on your local machine. It is necessary for code convention.
