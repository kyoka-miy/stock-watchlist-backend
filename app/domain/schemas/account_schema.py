from pydantic import BaseModel, EmailStr


class AccountSchema(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: str
    google_id: str

    class Config:
        orm_mode = True

class AccountCreateSchema(BaseModel):
    name: str
    email: EmailStr

    class Config:
        orm_mode = True
