from pydantic import BaseModel


class PricePointSchema(BaseModel):
    date: str
    close: float


class StockPriceHistoryResponse(BaseModel):
    symbol: str
    period: str
    interval: str
    points: list[PricePointSchema]
