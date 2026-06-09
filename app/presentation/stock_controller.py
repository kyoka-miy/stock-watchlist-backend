from fastapi import APIRouter, Depends, Query

from app.usecase.stock_usecase import StockUseCase
from app.domain.schemas.stock_search_response import StockSearchResponse

router = APIRouter(tags=["Stocks"], prefix="/stocks")


@router.get("/search", response_model=list[StockSearchResponse])
def search_stocks(q: str = Query(..., min_length=1), usecase: StockUseCase = Depends()):
    return usecase.search_stocks(q)
