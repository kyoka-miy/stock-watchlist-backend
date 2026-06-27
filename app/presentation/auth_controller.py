from fastapi import APIRouter, Depends, Response

from app.domain.schemas.google_login_request import GoogleLoginRequest
from app.domain.schemas.login_response import LoginResponse
from app.domain.schemas.logout_response import MessageResponse
from app.usecase.auth_usecase import AuthUseCase


router = APIRouter(tags=["Auth"], prefix="/auth")


@router.post("/google", response_model=LoginResponse)
def google_login(request: GoogleLoginRequest, response: Response, usecase: AuthUseCase = Depends(AuthUseCase)):
    return usecase.google_login(request.id_token, response)


@router.post("/logout", response_model=MessageResponse)
def logout(response: Response, usecase: AuthUseCase = Depends(AuthUseCase)):
    return usecase.logout(response)
