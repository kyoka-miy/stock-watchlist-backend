from fastapi import Depends

import pandas as pd

from app.domain.schemas.stock_search_response import StockSearchResponse
from app.domain.schemas.stock_price_history_response import PricePointSchema, StockPriceHistoryResponse
from app.domain.schemas.stock_dividend_history_response import StockDividendHistoryResponse
from app.domain.schemas.stock_cashflow_history_response import StockCashflowHistoryResponse
from app.domain.schemas.stock_performance_history_response import StockPerformanceHistoryResponse

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

    def get_price_history(self, symbol: str, period: str, interval: str) -> StockPriceHistoryResponse:
        points = self.stock_info_provider.get_price_history(
            symbol, period, interval)
        return StockPriceHistoryResponse(
            symbol=symbol,
            period=period,
            interval=interval,
            points=points,
        )

    def get_dividend_history(self, symbol: str, years: int) -> StockDividendHistoryResponse:
        points = self.stock_info_provider.get_dividend_history(symbol, years)

        average_dividend_per_share = None
        latest_dividend_yield = None
        growth_rate_percent = None
        average_payout_ratio = None

        if points:
            average_dividend_per_share = round(
                sum(point.dividend_per_share for point in points) / len(points),
                2,
            )

            for point in reversed(points):
                if point.dividend_yield is not None:
                    latest_dividend_yield = point.dividend_yield
                    break

            payout_ratios = [
                p.payout_ratio for p in points if p.payout_ratio is not None]
            if payout_ratios:
                average_payout_ratio = round(
                    sum(payout_ratios) / len(payout_ratios),
                    2,
                )

        if len(points) >= 2 and points[0].dividend_per_share > 0:
            growth_rate_percent = round(
                ((points[-1].dividend_per_share /
                 points[0].dividend_per_share) - 1) * 100,
                2,
            )

        return StockDividendHistoryResponse(
            symbol=symbol,
            years=years,
            points=points,
            average_dividend_per_share=average_dividend_per_share,
            latest_dividend_yield=latest_dividend_yield,
            growth_rate_percent=growth_rate_percent,
            average_payout_ratio=average_payout_ratio,
        )

    def get_cashflow_history(self, symbol: str, years: int) -> StockCashflowHistoryResponse:
        points = self.stock_info_provider.get_cashflow_history(symbol, years)
        return StockCashflowHistoryResponse(
            symbol=symbol,
            years=years,
            points=points,
        )

    def get_performance_history(self, symbol: str, years: int) -> StockPerformanceHistoryResponse:
        points = self.stock_info_provider.get_performance_history(
            symbol, years)

        revenue_growth_percent = None
        operating_margin_percent = None
        net_income_growth_percent = None

        if len(points) >= 2:
            first = points[0]
            last = points[-1]

            if first.revenue is not None and first.revenue > 0 and last.revenue is not None:
                revenue_growth_percent = round(
                    ((last.revenue / first.revenue) - 1) * 100,
                    2,
                )

            if first.net_income is not None and first.net_income > 0 and last.net_income is not None:
                net_income_growth_percent = round(
                    ((last.net_income / first.net_income) - 1) * 100,
                    2,
                )

        if points:
            latest = points[-1]
            if latest.revenue is not None and latest.revenue > 0 and latest.operating_income is not None:
                operating_margin_percent = round(
                    (latest.operating_income / latest.revenue) * 100,
                    2,
                )

        return StockPerformanceHistoryResponse(
            symbol=symbol,
            years=years,
            points=points,
            revenue_growth_percent=revenue_growth_percent,
            operating_margin_percent=operating_margin_percent,
            net_income_growth_percent=net_income_growth_percent,
        )

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
