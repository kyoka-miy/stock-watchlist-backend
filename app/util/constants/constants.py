from app.util.enum.yfinance_info_keys import YFinanceInfoKeys


class Constants:
    ALLOWED_EXCHANGES = frozenset({"JPX", "NYQ", "NMS", "NASDAQ", "NYSE"})

    SYMBOL = YFinanceInfoKeys.SYMBOL.value
    NAME = YFinanceInfoKeys.NAME.value
    EXCHANGE = YFinanceInfoKeys.EXCHANGE.value
    CURRENT_PRICE = YFinanceInfoKeys.CURRENT_PRICE.value
    PER = YFinanceInfoKeys.PER.value
    PBR = YFinanceInfoKeys.PBR.value
    DIVIDEND_YIELD = YFinanceInfoKeys.DIVIDEND_YIELD.value

    def __new__(cls, *args, **kwargs):
        raise TypeError("Constants class cannot be instantiated")

    def __setattr__(self, key, value):
        raise AttributeError("Constants values cannot be changed")

    def __delattr__(self, key):
        raise AttributeError("Constants values cannot be deleted")
