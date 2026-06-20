from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models.account import Account

class AccountRepository(ABC):
    @abstractmethod
    def get_accounts(self) -> List[Account]:
        pass

    @abstractmethod
    def create_account(self, account: Account) -> Account:
        pass

    @abstractmethod
    def get_account_by_id(self, id: int) -> Optional[Account]:
        pass

    @abstractmethod
    def update_account(self, account: Account) -> Account:
        pass

    @abstractmethod
    def delete_account(self, id: int):
        pass

    @abstractmethod
    def get_account_by_google_id(self, google_id: str) -> Optional[Account]:
        pass

    @abstractmethod
    def create_account_with_google_id(self, google_id: str, name: str, email: str) -> Account:
        pass
