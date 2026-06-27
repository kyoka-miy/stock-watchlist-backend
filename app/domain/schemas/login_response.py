from pydantic import BaseModel


class LoginResponse(BaseModel):
    access_token: str
    name: str
    email: str