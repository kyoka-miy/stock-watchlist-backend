from app.domain.schemas.login_response import LoginResponse
from app.service.dependencies import get_account_service
from fastapi import Depends
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import jwt

from app.config import settings
from app.service.account_service import AccountService


class AuthUseCase:
    def __init__(self, account_service: AccountService = Depends(get_account_service)):
        self.account_service = account_service

    def google_login(self, idToken: str) -> LoginResponse:
        payload = id_token.verify_oauth2_token(
            idToken,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        google_id = payload.get("sub")

        account = self.account_service.get_account_by_google_id(google_id)
        if not account:
            account = self.account_service.create_account(
                google_id, payload.get("name"), payload.get("email"))

        jwt_payload = {
            "sub": str(account.id)
        }

        access_token = jwt.encode(
            jwt_payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return LoginResponse(access_token=access_token)
