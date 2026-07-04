from pydantic import BaseModel


class DividendHistoryPointSchema(BaseModel):
    year: int
    dividend_per_share: float
    dividend_yield: float | None
    payout_ratio: float | None


class StockDividendHistoryResponse(BaseModel):
    symbol: str
    years: int
    points: list[DividendHistoryPointSchema]
    average_dividend_per_share: float | None
    latest_dividend_yield: float | None
    growth_rate_percent: float | None
    average_payout_ratio: float | None
