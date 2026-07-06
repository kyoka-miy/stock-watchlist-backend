from app.domain.schemas.login_response import LoginResponse
from app.domain.schemas.logout_response import MessageResponse
from app.service.dependencies import get_account_service
from fastapi import Depends, Response
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import jwt
from datetime import datetime, timedelta, timezone

from app.config import settings
from app.exceptions.app_exception import AppException
from app.service.account_service import AccountService


class AuthUseCase:
    def __init__(self, account_service: AccountService = Depends(get_account_service)):
        self.account_service = account_service

    def google_login(self, idToken: str, response: Response) -> LoginResponse:
        try:
            payload = id_token.verify_oauth2_token(
                idToken,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
        except ValueError as e:
            raise AppException("Invalid Google ID token") from e

        google_id = payload.get("sub")
        if not google_id:
            raise AppException("Google account ID is missing from token")

        account = self.account_service.get_account_by_google_id(google_id)
        if not account:
            account = self.account_service.create_account(
                google_id, payload.get("name"), payload.get("email"))

        access_token = self._create_access_token(account.id)
        refresh_token = self.create_refresh_token(account.id)

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 30,
        )

        return LoginResponse(access_token=access_token, name=payload.get("name"), email=payload.get("email"))

    def _create_access_token(self, account_id: int) -> str:
        payload = {
            "sub": str(account_id),
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
        }

        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    def create_refresh_token(self, account_id: int) -> str:
        payload = {
            "sub": str(account_id),
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(days=30),
        }

        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    def logout(self, response: Response) -> MessageResponse:
        response.delete_cookie(
            key="refresh_token",
            httponly=True,
            secure=True,
            samesite="lax",
        )
        return MessageResponse(message="Logged out successfully")
