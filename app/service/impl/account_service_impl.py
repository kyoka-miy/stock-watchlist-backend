from typing import Optional

from fastapi import Depends

from app.domain.schemas.account_schema import AccountSchema
from app.repository.account_repository import AccountRepository
from app.repository.dependencies import get_account_repository
from app.service.account_service import AccountService


class AccountServiceImpl(AccountService):
    def __init__(self, account_repository: AccountRepository = Depends(get_account_repository)):
        self.account_repository = account_repository

    def get_account_by_google_id(self, google_id: str) -> Optional[AccountSchema]:
        return self.account_repository.get_account_by_google_id(google_id)

    def create_account(self,  google_id: str, name: str, email: str) -> AccountSchema:
        return self.account_repository.create_account_with_google_id(google_id, name, email)