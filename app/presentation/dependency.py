from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
import jwt
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)


async def get_account_id_from_token(
    token: str = Depends(oauth2_scheme),
) -> int:

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        account_id = payload.get("sub")

        if account_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        account_id = int(account_id)

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    except ValueError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return account_id
