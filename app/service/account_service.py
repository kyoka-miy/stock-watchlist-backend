from abc import ABC, abstractmethod
from typing import Optional

from app.domain.schemas.account_schema import AccountSchema


class AccountService(ABC):
    @abstractmethod
    def get_account_by_google_id(self, google_id: str) -> Optional[AccountSchema]:
        pass

    @abstractmethod
    def create_account(self, google_id: str, name: str, email: str) -> AccountSchema:
        pass    