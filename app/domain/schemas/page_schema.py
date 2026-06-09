from typing import Generic, TypeVar
from pydantic import BaseModel, Field, model_validator

T = TypeVar('T')


class PageSchema(BaseModel, Generic[T]):
    pageNumber: int = 1
    pageSize: int = 20
    total: int = 0
    items: list[T] = []

    @model_validator(mode='before')
    @classmethod
    def paginate_items(cls, data):
        if isinstance(data, dict):
            items = data.get('items', [])
            pageNumber = data.get('pageNumber', 1)
            pageSize = data.get('pageSize', 20)

            total = len(items)
            offset = (pageNumber - 1) * pageSize
            paged_items = items[offset:offset + pageSize]

            data['total'] = total
            data['items'] = paged_items
        return data
