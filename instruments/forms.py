from typing import Optional

from pydantic import BaseModel


class LoginForm(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None


class RegisterForm(BaseModel):
    first_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: Optional[str]
    refresh_token: Optional[str]
    token_type: Optional[str] = "bearer"


class UserForm(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
