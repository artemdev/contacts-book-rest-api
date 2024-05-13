from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr


class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    birthday: date
    additional_note: str


class ContactModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    birthday: date
    additional_note: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)


class UserResponse(BaseModel):
    id: int = 1
    username: str
    email: EmailStr
    avatar: str

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
