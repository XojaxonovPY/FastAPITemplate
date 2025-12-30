from typing import Optional

from pydantic import BaseModel, Field


class LoginSchema(BaseModel):
    username: str
    password: str


class RegisterSchema(BaseModel):
    first_name: Optional[str] = None
    username: str
    password: str = Field(max_length=10, min_length=3)


class UserSchema(BaseModel):
    first_name: Optional[str] = None
    password: Optional[str] = None
    username: Optional[str] = None
