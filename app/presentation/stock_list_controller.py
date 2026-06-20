from fastapi import APIRouter, Depends

from app.domain.schemas.stock_list_name_account_id_request import StockListNameRequest
from app.domain.schemas.stock_list_schema import StockListSchema
from app.domain.schemas.stock_list_with_count_schema import StockListWithCountSchema
from app.domain.schemas.stock_list_with_stocks_schema import StockListWithStocksSchema
from app.domain.schemas.stock_list_name_request import StockListNameRequest
from app.domain.schemas.stock_list_symbols_request import StockListSymbolsRequest

from fastapi.responses import JSONResponse
from app.presentation.dependency import get_account_id_from_token
from app.usecase.stock_list_usecase import StockListUseCase
from app.util.enum.sort_orders import SortOrders


router = APIRouter(tags=["Stock Lists"], prefix="/stock-lists")


@router.post("/", response_model=StockListSchema)
def create_stock_list(request: StockListNameRequest, usecase: StockListUseCase = Depends(StockListUseCase), account_id: int = Depends(get_account_id_from_token)):
    return usecase.create_stock_list(request.name, account_id)


@router.put("/{stock_list_id}")
def update_name(stock_list_id: int, request: StockListNameRequest, usecase: StockListUseCase = Depends(StockListUseCase), account_id: int = Depends(get_account_id_from_token)):
    usecase.update_stock_list(stock_list_id, request.name, account_id)


@router.post("/{stock_list_id}/stocks")
def add_symbols_to_stock_list(stock_list_id: int, request: StockListSymbolsRequest, usecase: StockListUseCase = Depends(StockListUseCase), account_id: int = Depends(get_account_id_from_token)):
    usecase.add_symbols_to_list(stock_list_id, request.symbols, account_id)
    return JSONResponse(content={"message": "Symbols added to the list successfully"})


@router.delete("/{stock_list_id}/stocks")
def remove_symbols_from_stock_list(stock_list_id: int, request: StockListSymbolsRequest, usecase: StockListUseCase = Depends(StockListUseCase), account_id: int = Depends(get_account_id_from_token)):
    usecase.remove_symbols_from_list(
        stock_list_id, request.symbols, account_id)
    return JSONResponse(content={"message": "Symbols removed from the list successfully"})


@router.delete("/{stock_list_id}")
def delete_stock_list(stock_list_id: int, usecase: StockListUseCase = Depends(StockListUseCase), account_id: int = Depends(get_account_id_from_token)):
    usecase.delete_list(stock_list_id, account_id)
    return JSONResponse(content={"message": "Stock list deleted successfully"})


@router.get("/count", response_model=list[StockListWithCountSchema])
def get_all_stock_lists(account_id: int = Depends(get_account_id_from_token), usecase: StockListUseCase = Depends(StockListUseCase)):
    return usecase.get_all_stock_lists(account_id)


@router.get("/{stock_list_id}", response_model=StockListWithStocksSchema)
def get_stock_list_with_indicators_by_id(
    stock_list_id: int,
    pageSize: int = 20,
    pageNumber: int = 1,
    sortKey: str = "symbol",
    sortOrder: SortOrders = SortOrders.ASC,
    usecase: StockListUseCase = Depends(StockListUseCase),
    account_id: int = Depends(get_account_id_from_token)
):
    return usecase.get_stock_list_with_indicators(
        stock_list_id,
        pageSize,
        pageNumber,
        sortKey,
        sortOrder,
        account_id
    )
