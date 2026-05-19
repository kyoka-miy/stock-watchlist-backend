from pydantic import BaseModel


class StockListNameAccountIdRequest(BaseModel):
    name: str
    account_id: int
