import logging

from yfinance import Ticker
import yfinance as yf

from app.db.redis_cache import redis_cache
from app.exceptions.app_exception import AppException
from app.service.stock_info_provider import StockInfoProvider
from app.util.constants.constants import Constants
from app.util.japanese_stock_csv_utils import (
    get_japanese_industry_by_symbol,
    get_japanese_market_by_symbol,
    get_japanese_name_by_symbol,
)


class YFinanceInfoProviderImpl(StockInfoProvider):
    def get_valid_symbols(self, symbols: list[str]) -> list[str]:
        valid_symbols = []
        for symbol in symbols:
            ticker = Ticker(symbol)
            try:
                info = ticker.info
                if info.get(Constants.SYMBOL) == symbol:
                    valid_symbols.append(symbol)
            except Exception:
                continue
        return valid_symbols

    def get_stock_info(self, symbol: str) -> dict | None:
        if (redis_cache.get(symbol)):
            return redis_cache.get(symbol)

        info = None
        try:
            ticker = Ticker(symbol)
            info = ticker.info

            if (self._isJapaneseStock(symbol)):
                japaneseName = get_japanese_name_by_symbol(symbol)
                info[Constants.NAME] = japaneseName
                japaneseIndustry = get_japanese_industry_by_symbol(symbol)
                if japaneseIndustry is not None:
                    info[Constants.INDUSTRY] = japaneseIndustry
                japaneseMarket = get_japanese_market_by_symbol(symbol)
                if japaneseMarket is not None:
                    info[Constants.MARKET] = japaneseMarket
            redis_cache.set(symbol, info)
        except Exception:
            raise AppException(
                f"Failed to fetch stock info for symbol: {symbol}")

        return info

    def search_symbols_by_query(self, query: str) -> list[dict[str, str]]:
        results = []
        try:
            search_results = yf.Search(query, max_results=10).quotes
            for result in search_results:
                if result.get(Constants.EXCHANGE) in Constants.ALLOWED_EXCHANGES:
                    results.append(
                        {Constants.SYMBOL: result[Constants.SYMBOL], Constants.NAME: result.get("shortname")})
        except Exception:
            raise AppException(f"Failed to search stocks for query: {query}")

        return results

    def get_stock_infos_by_symbols(self, symbols: list[str]) -> list[dict]:
        infos = []
        for symbol in symbols:
            info = self.get_stock_info(symbol)
            if info is None:
                continue
            if info.get(Constants.SYMBOL) == symbol \
                    and info.get(Constants.CURRENT_PRICE) is not None \
                    and info.get(Constants.NAME) is not None:
                infos.append(info)

        return infos

    def _isJapaneseStock(self, symbol: str) -> bool:
        return symbol.endswith(".T")
