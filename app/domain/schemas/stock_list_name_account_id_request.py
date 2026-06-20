from pydantic import BaseModel


class StockListNameRequest(BaseModel):
    name: str
