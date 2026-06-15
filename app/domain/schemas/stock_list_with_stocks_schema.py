from pydantic import BaseModel, field_serializer

from app.domain.schemas.page_schema import PageSchema
from app.util.number_utils import NumberUtils


class StockInfoSchema(BaseModel):
    symbol: str
    name: str
    current_price: float | None
    price_change_ratio: float | None
    volume: float | None
    market_cap: float | None
    per: float | None
    pbr: float | None
    roe: float | None
    roa: float | None
    operating_margin: float | None
    revenue_growth: float | None
    earnings_growth: float | None
    profit_growth: float | None
    current_ratio: float | None
    dividend_yield: float | None
    dividend_per_share: float | None
    payout_ratio: float | None
    free_cash_flow: float | None
    industry: str | None
    market: str | None

    @field_serializer("current_price", "dividend_per_share", when_used="json")
    def serialize_currency(self, value: float | None):
        return NumberUtils.format_yen(value)

    @field_serializer("volume", "market_cap", "free_cash_flow", when_used="json")
    def serialize_compact_volume(self, value: float | None):
        return NumberUtils.format_compact_number(value)

    @field_serializer(
        "roe",
        "roa",
        "payout_ratio",
        "operating_margin",
        "revenue_growth",
        "earnings_growth",
        "profit_growth",
        when_used="json",
    )
    def serialize_percent(self, value: float | None):
        return NumberUtils.format_percent(value, ratio=True)

    @field_serializer("price_change_ratio", when_used="json")
    def serialize_price_change_ratio(self, value: float | None):
        return NumberUtils.format_percent(value, ratio=True, with_sign=True)

    @field_serializer(
        "dividend_yield",
        when_used="json",
    )
    def serialize_dividend_yield(self, value: float | None):
        return NumberUtils.add_percent_sign(value)


class StockListWithStocksSchema(BaseModel):
    name: str
    stocks: PageSchema[StockInfoSchema]
