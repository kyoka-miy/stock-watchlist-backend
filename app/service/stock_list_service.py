from abc import ABC, abstractmethod
from app.domain.models.stock_list import StockList
from app.domain.schemas.stock_list_schema import StockListSchema
from app.domain.schemas.stock_list_with_count_schema import StockListWithCountSchema


class StockListService(ABC):
    @abstractmethod
    def get_stock_list_by_id(self, stock_list_id: int, account_id: int) -> StockList:
        pass

    @abstractmethod
    def get_all_lists_with_count(self, account_id: int) -> list[StockListWithCountSchema]:
        pass

    @abstractmethod
    def update_stock_list_name(self, stock_list_id: int, name: str) -> None:
        pass

    @abstractmethod
    def create_stock_list(self, stock_list: StockList) -> StockListSchema:
        pass

    @abstractmethod
    def delete_list(self, stock_list_id: int, account_id: int) -> None:
        pass
