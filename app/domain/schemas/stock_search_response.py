from pydantic import BaseModel


class StockSearchResponse(BaseModel):
    symbol: str
    name: str
    current_price: float | None
    per: float | None
    pbr: float | None
    dividend_yield: float | None
