from fastapi import APIRouter, Depends

from app.domain.schemas.stock_list_name_account_id_request import StockListNameAccountIdRequest
from app.domain.schemas.stock_list_with_count_schema import StockListWithCountSchema
from app.domain.schemas.stock_list_with_stocks_schema import StockListWithStocksSchema
from app.domain.schemas.stock_list_name_request import StockListNameRequest
from app.domain.schemas.stock_list_symbols_request import StockListSymbolsRequest

from fastapi.responses import JSONResponse
from app.usecase.stock_list_usecase import StockListUseCase
from app.util.constants.sort_order_constants import SortOrderConstants


router = APIRouter(tags=["Stock Lists"], prefix="/stock-lists")

# TODO: fix


@router.post("/")
def create_stock_list(request: StockListNameAccountIdRequest, usecase: StockListUseCase = Depends(StockListUseCase)):
    usecase.create_stock_list(request.name, request.account_id)


@router.put("/{id}")
def update_name(id: int, request: StockListNameRequest, usecase: StockListUseCase = Depends(StockListUseCase)):
    usecase.update_stock_list(id, request.name)


@router.post("/{id}/stocks")
def add_symbols_to_stock_list(id: int, request: StockListSymbolsRequest, usecase: StockListUseCase = Depends(StockListUseCase)):
    usecase.add_symbols_to_list(id, request.symbols)
    return JSONResponse(content={"message": "Symbols added to the list successfully"})


@router.delete("/{id}/stocks")
def remove_symbols_from_stock_list(id: int, request: StockListSymbolsRequest, usecase: StockListUseCase = Depends(StockListUseCase)):
    usecase.remove_symbols_from_list(id, request.symbols)
    return JSONResponse(content={"message": "Symbols removed from the list successfully"})


@router.delete("/{id}")
def delete_stock_list(id: int, usecase: StockListUseCase = Depends(StockListUseCase)):
    usecase.delete_list(id)
    return JSONResponse(content={"message": "Stock list deleted successfully"})


@router.get("/{id}", response_model=StockListWithStocksSchema)
def get_stock_list_with_indicators_by_id(
    id: int,
    pageSize: int = 20,
    pageNumber: int = 1,
    sortKey: str = "symbol",
    sortOrder: SortOrderConstants = SortOrderConstants.ASC,
    usecase: StockListUseCase = Depends(StockListUseCase)
):
    return usecase.get_stock_list_with_indicators(
        id,
        pageSize=pageSize,
        pageNumber=pageNumber,
        sortKey=sortKey,
        sortOrder=sortOrder
    )


@router.get("/count/{account_id}", response_model=list[StockListWithCountSchema])
def get_all_stock_lists(account_id: int, usecase: StockListUseCase = Depends(StockListUseCase)):
    return usecase.get_all_stock_lists(account_id)
