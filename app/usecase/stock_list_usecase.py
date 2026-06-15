from concurrent.futures import ThreadPoolExecutor, as_completed
from app.domain.schemas.stock_list_schema import StockListSchema
from app.domain.schemas.stock_list_with_count_schema import StockListWithCountSchema
from app.service.stock_info_provider import StockInfoProvider
from app.util.constants.constants import Constants
from app.util.number_utils import NumberUtils
from app.db.redis_cache import redis_cache

from fastapi import Depends

from app.domain.models.stock_list import StockList
from app.domain.schemas.page_schema import PageSchema
from app.domain.schemas.stock_list_with_stocks_schema import StockListWithStocksSchema, StockInfoSchema
from app.service.dependencies import get_stock_info_provider, get_stock_list_service, get_stock_list_stock_service
from app.service.impl.stock_list_service_impl import StockListService
from app.service.impl.stock_list_stock_service_impl import StockListStockService

from app.util.enum.sort_orders import SortOrders


class StockListUseCase:
    def __init__(
            self,
            stock_list_service: StockListService = Depends(
                get_stock_list_service),
            stock_list_stock_service: StockListStockService = Depends(
                get_stock_list_stock_service),
            stock_info_provider: StockInfoProvider = Depends(get_stock_info_provider)):
        self.stock_list_service = stock_list_service
        self.stock_list_stock_service = stock_list_stock_service
        self.stock_info_provider = stock_info_provider

    def create_stock_list(self, name: str, account_id: int) -> StockListSchema:
        return self.stock_list_service.create_stock_list(
            StockList(name=name, account_id=account_id))

    def update_stock_list(self, stock_list_id: int, name: str) -> None:
        self.stock_list_service.get_stock_list_by_id(
            stock_list_id)

        self.stock_list_service.update_stock_list_name(stock_list_id, name)

    def add_symbols_to_list(self, stock_list_id: int, symbols: list[str]) -> None:
        self.stock_list_service.get_stock_list_by_id(stock_list_id)

        not_registered_symbols = self.stock_list_stock_service.get_not_registered_symbols(
            stock_list_id, symbols)

        # get valid symbols by yfinance
        valid_symbols = self.stock_info_provider.get_valid_symbols(
            not_registered_symbols)

        self.stock_list_stock_service.add_symbols_to_list(
            stock_list_id, valid_symbols)

    def remove_symbols_from_list(self, stock_list_id: int, symbols: list[str]) -> None:
        self.stock_list_service.get_stock_list_by_id(stock_list_id)

        self.stock_list_stock_service.remove_symbols_from_list(
            stock_list_id, symbols)

    def delete_list(self, stock_list_id: int) -> None:
        self.stock_list_service.get_stock_list_by_id(stock_list_id)

        # Delete all related records from stock_list_stock first
        self.stock_list_stock_service.delete_list(
            stock_list_id)

        # Then delete the stock list itself
        self.stock_list_service.delete_list(stock_list_id)

    def get_stock_list_with_indicators(self, stock_list_id: int, pageSize: int, pageNumber: int, sortKey: str, sortOrder: SortOrders) -> StockListWithStocksSchema:
        stock_list = self.stock_list_service.get_stock_list_by_id(
            stock_list_id)

        symbols = self.stock_list_stock_service.get_symbols_by_list_id(
            stock_list_id)
        stocks: list[StockInfoSchema] = []

        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_symbol = {executor.submit(
                self._fetch_info, symbol): symbol for symbol in symbols}

            for future in as_completed(future_to_symbol):
                symbol, info = future.result()
                if not info or info.get(Constants.NAME) is None:
                    continue

                current_price = info.get(Constants.CURRENT_PRICE)
                previous_close = info.get(Constants.PREVIOUS_CLOSE)
                price_change_ratio = None
                if isinstance(current_price, (int, float)) and isinstance(previous_close, (int, float)):
                    if previous_close != 0:
                        price_change_ratio = (
                            current_price - previous_close) / previous_close

                stocks.append(StockInfoSchema(
                    symbol=symbol,
                    name=info.get(Constants.NAME),
                    current_price=current_price,
                    price_change_ratio=price_change_ratio,
                    volume=info.get(Constants.VOLUME),
                    market_cap=info.get(Constants.MARKET_CAP),
                    dividend_yield=info.get(Constants.DIVIDEND_YIELD),
                    dividend_per_share=info.get(Constants.DIVIDEND_PER_SHARE),
                    payout_ratio=info.get(Constants.PAYOUT_RATIO),
                    per=NumberUtils.get_round(info.get(Constants.PER)),
                    pbr=NumberUtils.get_round(info.get(Constants.PBR)),
                    roe=info.get(Constants.ROE),
                    roa=info.get(Constants.ROA),
                    operating_margin=info.get(Constants.OPERATING_MARGIN),
                    revenue_growth=info.get(Constants.REVENUE_GROWTH),
                    earnings_growth=info.get(Constants.EARNINGS_GROWTH),
                    profit_growth=info.get(Constants.PROFIT_GROWTH),
                    current_ratio=NumberUtils.get_round(
                        info.get(Constants.CURRENT_RATIO)),
                    free_cash_flow=info.get(Constants.FREE_CASH_FLOW),
                    market=info.get(Constants.MARKET),
                    sector=info.get(Constants.SECTOR),
                    industry=info.get(Constants.INDUSTRY)
                ))

        reverse = sortOrder == SortOrders.DESC
        stocks.sort(key=lambda x: self._sort_key(x, sortKey), reverse=reverse)

        return StockListWithStocksSchema(
            name=stock_list.name,
            stocks=PageSchema[StockInfoSchema](
                pageNumber=pageNumber,
                pageSize=pageSize,
                items=stocks
            )
        )

    def get_all_stock_lists(self, account_id: int) -> list[StockListWithCountSchema]:
        stock_lists = self.stock_list_service.get_all_lists_with_count(
            account_id)
        return [StockListWithCountSchema(id=stock_list.id, name=stock_list.name, count=stock_list.count) for stock_list in stock_lists]

    def _fetch_info(self, symbol) -> tuple[str, dict | None]:
        return symbol, self.stock_info_provider.get_stock_info(symbol)

    def _sort_key(self, x: StockInfoSchema, sortKey: str):
        value = getattr(x, sortKey, None)
        # None always will be at the end
        if value is None:
            return (1,)
        return (0, value)
