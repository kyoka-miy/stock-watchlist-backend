from fastapi import Depends

import pandas as pd

from app.domain.schemas.stock_search_response import StockSearchResponse
from app.domain.schemas.stock_price_history_response import PricePointSchema, StockPriceHistoryResponse

from app.exceptions.app_exception import AppException
from app.service.dependencies import get_stock_info_provider
from app.service.stock_info_provider import StockInfoProvider
from app.util.constants.constants import Constants
from app.util.enum.yfinance_info_keys import YFinanceInfoKeys
from app.util.number_utils import NumberUtils


class StockUseCase:

    _YAHOO_URL_BASE = "https://finance.yahoo.com/quote/"
    _IRBANK_URL_BASE = "https://irbank.net/"
    _BUFFETT_CODE_URL_BASE = "https://www.buffett-code.com/company/"

    def __init__(
            self, stock_info_provider: StockInfoProvider = Depends(get_stock_info_provider)):
        self.stock_info_provider = stock_info_provider

    def search_stocks(self, query: str) -> list[StockSearchResponse]:
        symbolAndNames: list[dict[str, str]] = []
        if any(ord(c) > 127 or c == ' ' for c in query):
            symbolAndNames += self._search_csv(query)

        symbolAndNames += self._search_api(query)

        infos = self.stock_info_provider.get_stock_infos_by_symbols(
            [item[Constants.SYMBOL] for item in symbolAndNames])

        return [
            StockSearchResponse(
                symbol=info.get(Constants.SYMBOL),
                name=info.get(Constants.NAME),
                current_price=info.get(Constants.CURRENT_PRICE),
                per=NumberUtils.get_round(info.get(Constants.PER)),
                pbr=NumberUtils.get_round(info.get(Constants.PBR)),
                dividend_yield=NumberUtils.get_round(
                    info.get(Constants.DIVIDEND_YIELD)),
            )
            for info in infos if info
        ]

    def _search_csv(self, query: str) -> list[dict[str, str]]:
        results = []
        try:
            df = pd.read_csv("app/data/data_j.csv")
            matched = df[df["銘柄名"].str.contains(query, na=False)]

            for _, row in matched.head(10).iterrows():
                code = str(row["コード"])
                print(f"Matched row: コード={code}, 銘柄名={row['銘柄名']}")
                results.append({Constants.SYMBOL: f"{code}.T",
                               Constants.NAME: row["銘柄名"]})
        except Exception as e:
            raise AppException(f"Failed to search stocks from CSV: {e}") from e
        return results

    def _search_api(self, query: str) -> list[dict[str, str]]:
        return self.stock_info_provider.search_symbols_by_query(query)

    def get_price_history(self, symbol: str, period: str, interval: str) -> StockPriceHistoryResponse:
        points = self.stock_info_provider.get_price_history(
            symbol, period, interval)
        return StockPriceHistoryResponse(
            symbol=symbol,
            period=period,
            interval=interval,
            points=points,
        )
