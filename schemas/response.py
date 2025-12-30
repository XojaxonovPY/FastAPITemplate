from typing import Optional

from pydantic import BaseModel


class TokenResponseSchema(BaseModel):
    access_token: Optional[str]
    refresh_token: Optional[str]
    token_type: Optional[str] = "bearer"


class UserResponseSchema(BaseModel):
    id: Optional[int]
    first_name: Optional[str]
    username: Optional[str]
