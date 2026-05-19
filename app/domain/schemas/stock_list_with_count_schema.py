from pydantic import BaseModel


class StockListWithCountSchema(BaseModel):
    id: int
    name: str
    count: int

    class Config:
        orm_mode = True
