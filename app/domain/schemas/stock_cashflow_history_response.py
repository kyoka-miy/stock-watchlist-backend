from pydantic import BaseModel


class CashflowHistoryPointSchema(BaseModel):
    year: int
    operating_cashflow: float | None
    investing_cashflow: float | None
    financing_cashflow: float | None


class StockCashflowHistoryResponse(BaseModel):
    symbol: str
    years: int
    points: list[CashflowHistoryPointSchema]
