from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    username: str


class UserViewBase(BaseModel):
    id: int
    username: str
    full_name: str
    email: EmailStr
    is_active: bool


class UserCreateBase(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    password: str
    password_confirm: str


class UserUpdateBase(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserChangePasswordBase(BaseModel):
    old_password: str
    new_password: str
    new_password_confirm: str


class TokenAccessRefreshBase(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenAccessBase(BaseModel):
    access_token: str
    token_type: str = "bearer"
