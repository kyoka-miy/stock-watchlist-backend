import logging

from yfinance import Ticker
import yfinance as yf

from app.db.redis_cache import redis_cache
from app.domain.schemas.stock_price_history_response import PricePointSchema
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

    def get_price_history(self, symbol: str, period: str, interval: str) -> list[PricePointSchema]:
        """
        Fetch stock price history with Redis caching.
        Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        Valid intervals: 1m, 5m, 15m, 30m, 60m, 1h, 1d, 1wk, 1mo
        """
        cache_key = f"stock:price-history:{symbol}:{period}:{interval}"
        cached = redis_cache.get(cache_key)
        if cached is not None:
            return [PricePointSchema(**point) for point in cached]

        try:
            ticker = Ticker(symbol)
            history = ticker.history(period=period, interval=interval)
        except Exception as e:
            raise AppException(
                f"Failed to fetch price history for symbol: {symbol}") from e

        if history.empty:
            return []

        points: list[PricePointSchema] = []
        for index, row in history.iterrows():
            close_val = row.get("Close")
            if close_val is None:
                continue
            points.append(
                PricePointSchema(
                    date=index.isoformat(),
                    close=float(close_val),
                )
            )

        # Convert to dict for Redis caching (JSON serialization)
        points_dict = [point.model_dump() for point in points]
        redis_cache.set(cache_key, points_dict)
        return points

    def _isJapaneseStock(self, symbol: str) -> bool:
        return symbol.endswith(".T")
