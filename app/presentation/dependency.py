from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import InvalidTokenError

from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)


async def get_account_id_from_token(
    request: Request,
    response: Response,
    token: str = Depends(oauth2_scheme),
) -> int:

    def _decode_and_validate(token: str, expected_type: str) -> int:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        token_type = payload.get("type")
        account_id = payload.get("sub")

        if token_type != expected_type or account_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return int(account_id)

    try:
        return _decode_and_validate(token, "access")
    except (InvalidTokenError, ValueError, HTTPException) as e:
        print("Access token invalid or expired, trying refresh token...", str(e))
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="No refresh token")

        try:
            account_id = _decode_and_validate(refresh_token, "refresh")
        except (InvalidTokenError, ValueError, HTTPException):
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        print(f"Refresh token used for account_id: {account_id}")
        new_access_token = jwt.encode(
            {
                "sub": str(account_id),
                "type": "access",
                "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        response.headers["X-New-Access-Token"] = new_access_token
        return account_id
