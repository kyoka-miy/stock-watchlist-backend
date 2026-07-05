import logging
import math
from datetime import datetime, timezone

from yfinance import Ticker
import yfinance as yf

from app.db.redis_cache import redis_cache
from app.domain.schemas.stock_dividend_history_response import DividendHistoryPointSchema
from app.domain.schemas.stock_cashflow_history_response import CashflowHistoryPointSchema
from app.domain.schemas.stock_performance_history_response import PerformanceHistoryPointSchema
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

    def get_dividend_history(self, symbol: str, years: int) -> list[DividendHistoryPointSchema]:
        cache_key = f"stock:dividend-history:v2:{symbol}:{years}"
        cached = redis_cache.get(cache_key)
        if cached is not None:
            return [DividendHistoryPointSchema(**point) for point in cached]

        try:
            ticker = Ticker(symbol)
            dividends = ticker.dividends
            history = ticker.history(period="max", interval="1d")
            info = ticker.info
        except Exception as e:
            raise AppException(
                f"Failed to fetch dividend history for symbol: {symbol}") from e

        if dividends.empty:
            return []

        fiscal_year_end_month = self._get_fiscal_year_end_month(info)
        fiscal_year_labels = dividends.index.map(
            lambda d: d.year + 1 if d.month > fiscal_year_end_month else d.year
        )
        annual_dividends = dividends.groupby(fiscal_year_labels).sum()
        filtered_annual_dividends = annual_dividends[annual_dividends > 0].sort_index().tail(
            years)

        close_by_year = None
        if not history.empty:
            history_fiscal_year_labels = history.index.map(
                lambda d: d.year + 1 if d.month > fiscal_year_end_month else d.year
            )
            close_by_year = history.groupby(history_fiscal_year_labels)[
                "Close"].last()

        points: list[DividendHistoryPointSchema] = []
        for year, yearly_dividend in filtered_annual_dividends.items():
            dividend_per_share = float(yearly_dividend)

            dividend_yield = None
            if close_by_year is not None and year in close_by_year.index:
                year_end_close = close_by_year.loc[year]
                if (
                    year_end_close is not None
                    and not math.isnan(float(year_end_close))
                    and float(year_end_close) > 0
                ):
                    dividend_yield = round(
                        (dividend_per_share / float(year_end_close)) * 100,
                        2,
                    )

            payout_ratio = None
            if close_by_year is not None and year in close_by_year.index:
                try:
                    if info and info.get('trailingPE') is not None and info.get('trailingEps') is not None:
                        eps = info.get('trailingEps')
                        if eps and eps > 0:
                            payout_ratio = round(
                                (dividend_per_share / eps) * 100,
                                2,
                            )
                except Exception:
                    pass

            points.append(
                DividendHistoryPointSchema(
                    year=int(year),
                    dividend_per_share=round(dividend_per_share, 4),
                    dividend_yield=dividend_yield,
                    payout_ratio=payout_ratio,
                )
            )

        points_dict = [point.model_dump() for point in points]
        redis_cache.set(cache_key, points_dict)
        return points

    def get_cashflow_history(self, symbol: str, years: int) -> list[CashflowHistoryPointSchema]:
        cache_key = f"stock:cashflow-history:v1:{symbol}:{years}"
        cached = redis_cache.get(cache_key)
        if cached is not None:
            return [CashflowHistoryPointSchema(**point) for point in cached]

        try:
            ticker = Ticker(symbol)
            cashflow = ticker.cashflow
        except Exception as e:
            raise AppException(
                f"Failed to fetch cashflow history for symbol: {symbol}") from e

        if cashflow is None or cashflow.empty:
            return []

        points: list[CashflowHistoryPointSchema] = []

        # yfinance cashflow columns are fiscal period end dates.
        for fiscal_period_end in sorted(cashflow.columns):
            column = cashflow[fiscal_period_end]
            operating = column.get("Operating Cash Flow")
            investing = column.get("Investing Cash Flow")
            financing = column.get("Financing Cash Flow")

            if operating is None and investing is None and financing is None:
                continue

            points.append(
                CashflowHistoryPointSchema(
                    year=int(fiscal_period_end.year),
                    operating_cashflow=float(operating) if operating is not None and not math.isnan(
                        float(operating)) else None,
                    investing_cashflow=float(investing) if investing is not None and not math.isnan(
                        float(investing)) else None,
                    financing_cashflow=float(financing) if financing is not None and not math.isnan(
                        float(financing)) else None,
                )
            )

        points = points[-years:]
        points_dict = [point.model_dump() for point in points]
        redis_cache.set(cache_key, points_dict)
        return points

    def get_performance_history(self, symbol: str, years: int) -> list[PerformanceHistoryPointSchema]:
        cache_key = f"stock:performance-history:v1:{symbol}:{years}"
        cached = redis_cache.get(cache_key)
        if cached is not None:
            return [PerformanceHistoryPointSchema(**point) for point in cached]

        try:
            ticker = Ticker(symbol)
            financials = ticker.financials
            income_stmt = ticker.income_stmt
        except Exception as e:
            raise AppException(
                f"Failed to fetch performance history for symbol: {symbol}") from e

        statement = financials if financials is not None and not financials.empty else income_stmt
        if statement is None or statement.empty:
            return []

        points: list[PerformanceHistoryPointSchema] = []
        for fiscal_period_end in sorted(statement.columns):
            column = statement[fiscal_period_end]

            revenue = column.get("Total Revenue")
            if revenue is None:
                revenue = column.get("Operating Revenue")

            operating_income = column.get("Operating Income")
            net_income = column.get("Net Income")

            if revenue is None and operating_income is None and net_income is None:
                continue

            points.append(
                PerformanceHistoryPointSchema(
                    year=int(fiscal_period_end.year),
                    revenue=float(revenue) if revenue is not None and not math.isnan(
                        float(revenue)) else None,
                    operating_income=float(operating_income) if operating_income is not None and not math.isnan(
                        float(operating_income)) else None,
                    net_income=float(net_income) if net_income is not None and not math.isnan(
                        float(net_income)) else None,
                )
            )

        points = points[-years:]
        points_dict = [point.model_dump() for point in points]
        redis_cache.set(cache_key, points_dict)
        return points

    def _get_fiscal_year_end_month(self, info: dict | None) -> int:
        if not info:
            return 12

        fiscal_year_end_raw = info.get(
            "lastFiscalYearEnd") or info.get("nextFiscalYearEnd")
        if isinstance(fiscal_year_end_raw, (int, float)):
            try:
                return datetime.fromtimestamp(fiscal_year_end_raw, tz=timezone.utc).month
            except (OverflowError, OSError, ValueError):
                return 12

        return 12

    def _isJapaneseStock(self, symbol: str) -> bool:
        return symbol.endswith(".T")
