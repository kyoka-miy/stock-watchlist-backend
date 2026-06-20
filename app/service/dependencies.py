from app.service.account_service import AccountService
from app.service.impl.account_service_impl import AccountServiceImpl
from fastapi import Depends

from app.service import *
from app.service.impl import *
from app.service.impl.yfinance_info_provider_impl import YFinanceInfoProviderImpl
from app.service.stock_info_provider import StockInfoProvider


def get_stock_list_service(
        service: StockListServiceImpl = Depends(StockListServiceImpl),
) -> StockListService:
    return service

def get_stock_list_stock_service(
        service: StockListStockServiceImpl = Depends(StockListStockServiceImpl),
) -> StockListStockService:
    return service

def get_stock_info_provider(
        service: YFinanceInfoProviderImpl = Depends(YFinanceInfoProviderImpl),
) -> StockInfoProvider:
    return service

def get_account_service(
        service: AccountServiceImpl = Depends(AccountServiceImpl)
) -> AccountService:
    return service