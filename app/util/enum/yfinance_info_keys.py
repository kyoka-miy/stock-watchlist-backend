from enum import Enum


class YFinanceInfoKeys(str, Enum):
    SYMBOL = "symbol"
    NAME = "shortName"
    EXCHANGE = "exchange"
    CURRENT_PRICE = "currentPrice"
    PER = "trailingPE"
    PBR = "priceToBook"
    DIVIDEND_YIELD = "dividendYield"
