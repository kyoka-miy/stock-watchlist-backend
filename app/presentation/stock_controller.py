from fastapi import APIRouter, Depends, Query

from app.presentation.dependency import get_account_id_from_token
from app.domain.schemas.stock_price_history_response import StockPriceHistoryResponse
from app.domain.schemas.stock_dividend_history_response import StockDividendHistoryResponse
from app.domain.schemas.stock_cashflow_history_response import StockCashflowHistoryResponse
from app.domain.schemas.stock_performance_history_response import StockPerformanceHistoryResponse
from app.usecase.stock_usecase import StockUseCase
from app.domain.schemas.stock_search_response import StockSearchResponse

router = APIRouter(tags=["Stocks"], prefix="/stocks")


@router.get("/search", response_model=list[StockSearchResponse])
def search_stocks(q: str = Query(..., min_length=1), usecase: StockUseCase = Depends(), account_id: int = Depends(get_account_id_from_token)):
    return usecase.search_stocks(q)


@router.get("/{symbol}/price-history", response_model=StockPriceHistoryResponse)
def get_price_history(
    symbol: str,
    period: str = Query("1y"),
    interval: str = Query("1d"),
    usecase: StockUseCase = Depends(),
    account_id: int = Depends(get_account_id_from_token),
):
    return usecase.get_price_history(symbol, period, interval)


@router.get("/{symbol}/dividend-history", response_model=StockDividendHistoryResponse)
def get_dividend_history(
    symbol: str,
    years: int = Query(6, ge=1, le=20),
    usecase: StockUseCase = Depends(),
    account_id: int = Depends(get_account_id_from_token),
):
    return usecase.get_dividend_history(symbol, years)


@router.get("/{symbol}/cashflow-history", response_model=StockCashflowHistoryResponse)
def get_cashflow_history(
    symbol: str,
    years: int = Query(6, ge=1, le=20),
    usecase: StockUseCase = Depends(),
    account_id: int = Depends(get_account_id_from_token),
):
    return usecase.get_cashflow_history(symbol, years)


@router.get("/{symbol}/performance-history", response_model=StockPerformanceHistoryResponse)
def get_performance_history(
    symbol: str,
    years: int = Query(6, ge=1, le=20),
    usecase: StockUseCase = Depends(),
    account_id: int = Depends(get_account_id_from_token),
):
    return usecase.get_performance_history(symbol, years)
