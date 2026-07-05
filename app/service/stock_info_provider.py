from abc import ABC, abstractmethod
from app.domain.schemas.stock_price_history_response import PricePointSchema
from app.domain.schemas.stock_dividend_history_response import DividendHistoryPointSchema
from app.domain.schemas.stock_cashflow_history_response import CashflowHistoryPointSchema
from app.domain.schemas.stock_performance_history_response import PerformanceHistoryPointSchema


class StockInfoProvider(ABC):
    @abstractmethod
    def get_valid_symbols(self, symbols: list[str]) -> list[str]:
        pass

    @abstractmethod
    def get_stock_info(self, symbol: str) -> dict | None:
        pass

    @abstractmethod
    def search_symbols_by_query(self, query: str) -> list[str]:
        pass

    @abstractmethod
    def get_stock_infos_by_symbols(self, symbols: list[str]) -> list[dict]:
        pass

    @abstractmethod
    def get_price_history(self, symbol: str, period: str, interval: str) -> list[PricePointSchema]:
        pass

    @abstractmethod
    def get_dividend_history(self, symbol: str, years: int) -> list[DividendHistoryPointSchema]:
        pass

    @abstractmethod
    def get_cashflow_history(self, symbol: str, years: int) -> list[CashflowHistoryPointSchema]:
        pass

    @abstractmethod
    def get_performance_history(self, symbol: str, years: int) -> list[PerformanceHistoryPointSchema]:
        pass
