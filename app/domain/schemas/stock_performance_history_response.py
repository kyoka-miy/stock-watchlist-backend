from pydantic import BaseModel


class PerformanceHistoryPointSchema(BaseModel):
    year: int
    revenue: float | None
    operating_income: float | None
    net_income: float | None


class StockPerformanceHistoryResponse(BaseModel):
    symbol: str
    years: int
    points: list[PerformanceHistoryPointSchema]
    revenue_growth_percent: float | None
    operating_margin_percent: float | None
    net_income_growth_percent: float | None
