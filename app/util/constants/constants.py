from app.util.enum.yfinance_info_keys import YFinanceInfoKeys


class Constants:
    ALLOWED_EXCHANGES = frozenset({"JPX", "NYQ", "NMS", "NASDAQ", "NYSE"})

    SYMBOL = YFinanceInfoKeys.SYMBOL.value
    NAME = YFinanceInfoKeys.NAME.value
    EXCHANGE = YFinanceInfoKeys.EXCHANGE.value
    CURRENT_PRICE = YFinanceInfoKeys.CURRENT_PRICE.value
    PREVIOUS_CLOSE = YFinanceInfoKeys.PREVIOUS_CLOSE.value
    VOLUME = YFinanceInfoKeys.VOLUME.value
    MARKET_CAP = YFinanceInfoKeys.MARKET_CAP.value
    PER = YFinanceInfoKeys.PER.value
    PBR = YFinanceInfoKeys.PBR.value
    OPERATING_MARGIN = YFinanceInfoKeys.OPERATING_MARGIN.value
    REVENUE_GROWTH = YFinanceInfoKeys.REVENUE_GROWTH.value
    EARNINGS_GROWTH = YFinanceInfoKeys.EARNINGS_GROWTH.value
    PROFIT_GROWTH = YFinanceInfoKeys.PROFIT_GROWTH.value
    CURRENT_RATIO = YFinanceInfoKeys.CURRENT_RATIO.value
    DIVIDEND_YIELD = YFinanceInfoKeys.DIVIDEND_YIELD.value
    DIVIDEND_PER_SHARE = YFinanceInfoKeys.DIVIDEND_PER_SHARE.value
    PAYOUT_RATIO = YFinanceInfoKeys.PAYOUT_RATIO.value
    FREE_CASH_FLOW = YFinanceInfoKeys.FREE_CASH_FLOW.value
    ROE = YFinanceInfoKeys.ROE.value
    ROA = YFinanceInfoKeys.ROA.value
    MARKET = YFinanceInfoKeys.MARKET.value
    SECTOR = YFinanceInfoKeys.SECTOR.value
    INDUSTRY = YFinanceInfoKeys.INDUSTRY.value

    def __new__(cls, *args, **kwargs):
        raise TypeError("Constants class cannot be instantiated")

    def __setattr__(self, key, value):
        raise AttributeError("Constants values cannot be changed")

    def __delattr__(self, key):
        raise AttributeError("Constants values cannot be deleted")
