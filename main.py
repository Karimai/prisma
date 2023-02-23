import logging
import os
import sys
from datetime import datetime

from currencies import Currency
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator

from api import API
from helper import convert_date_string

logging.basicConfig(
    level=logging.INFO,  # or logging.DEBUG to see more detailed messages
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("./app-logs/app.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

load_dotenv()


class FxRateCurrency(BaseModel):
    stock_symbol: str  # Any valid ticket, for ex. AAPL. indicates the stocks ticker
    currency: str  # Any valid currency, for ex. EUR, USD. referencing the currency of price
    date_range: str  # two strings seperated with - (<start>-<end>), eg. 10.01.2022-10.02.2022

    @validator("currency")
    def validate_currency_code(cls, value):
        Currency(value)
        return value

    @validator("date_range")
    def validate_date(cls, value: str) -> str:
        """
        o Month-Day-Year with leading zeros (02/17/2009)
        o Day-Month-Year with leading zeros and dots as separators (17.02.2009)
        o Month name Day, Year like this (February 17, 2009)
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        %m: Month as a zero-padded decimal number; 01, 02, …, 12
        %B: Month as locale’s full name; January, February, …, December (en_US);
        %d: Day of the month as a zero-padded decimal number; 01, 02, …, 31
        %Y: Year with century as a decimal number; 0001, 0002, …, 2013, 2014, …, 9998, 9999
        """
        regex = datetime.strptime
        accepted_formats = ["%m/%d/%Y", "%d.%m.%Y", "%B %d, %Y"]
        start_date_str, end_date_str = value.split("-")
        for accepted_format in accepted_formats:
            try:
                start_date = regex(start_date_str.strip(), accepted_format)
                end_date = regex(end_date_str.strip(), accepted_format)
                if start_date <= end_date:
                    return value
            except ValueError:
                logger.info("value except")
                continue
        raise ValueError("Invalid date range format")


app = FastAPI()


@app.get("/")
async def root():
    """
    It is just for test. The only api is /stocks/. It takes an JSON object and return
    list of close rate for the given symbol in currency.
    :return:
    """
    return {"message": "test"}


@app.post("/stocks/", response_class=JSONResponse)
def get_stock_price(item: FxRateCurrency):
    """
    Retrieves the latest stock price for the given symbol from MarketStack API
    """
    base = "USD"
    start_date, end_date = item.date_range.split("-")
    start_date = convert_date_string(start_date)
    end_date = convert_date_string(end_date)

    exchange_rates_api = API(
        os.getenv("EXCHANGE_RATES_URL"),
        headers={"apikey": os.getenv("EXCHANGERATESAPI_ACCESS_KEY")},
    )
    exchange_rates_params = {
        "start_date": start_date,
        "end_date": end_date,
        "symbols": item.currency,
        "base": base,
    }
    exchange_rates_response = exchange_rates_api.get(exchange_rates_params)

    exchange_rates = [
        (dat, float(rates[item.currency]))
        for dat, rates in exchange_rates_response["rates"].items()
    ]

    marketstack_api = API(
        os.getenv("MARKETSTACK_BASE_URL"), headers={"Accept": "application/json"}
    )
    marketstack_params = {
        "symbols": item.stock_symbol,
        "access_key": f"{os.getenv('MARKETSTACK_API_KEY')}",
        "date_from": start_date,
        "date_to": end_date,
        "currency": base,
    }
    marketstack_response = marketstack_api.get(marketstack_params)

    daily_close = {}
    currency_rate = 1.0  # TODO, default for the first day when no exchange rate

    logger.info(f"Retrieved daily close prices: {daily_close}")
    for exchange_rate in exchange_rates:
        found: bool = False
        for stock_data in marketstack_response["data"]:
            if stock_data["date"][:10] == exchange_rate[0]:
                daily_close[stock_data["date"][:10]] = round(
                    stock_data["close"] * exchange_rate[1], 1
                )
                currency_rate = exchange_rate[1]
                found = True
                break
        if not found:
            daily_close[exchange_rate[0]] = round(
                stock_data["close"] * currency_rate, 1
            )
    logger.info(f"Retrieved daily close prices: {daily_close}")
    return {
        "symbol": item.stock_symbol,
        "currency": item.currency,
        "daily_close": daily_close,
    }
