from fastapi import APIRouter, Depends

from app.domain.schemas.google_login_request import GoogleLoginRequest
from app.domain.schemas.login_response import LoginResponse
from app.usecase.auth_usecase import AuthUseCase


router = APIRouter(tags=["Auth"], prefix="/auth")


@router.post("/google", response_model=LoginResponse)
def google_login(request: GoogleLoginRequest, usecase: AuthUseCase = Depends(AuthUseCase)):
    return usecase.google_login(request.id_token)