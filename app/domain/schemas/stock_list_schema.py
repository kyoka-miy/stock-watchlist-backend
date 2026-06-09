from pydantic import BaseModel


class StockListSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
