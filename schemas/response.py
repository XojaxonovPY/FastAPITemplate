from typing import Optional

from pydantic import BaseModel, ConfigDict


class TokenResponseSchema(BaseModel):
    access_token: Optional[str]
    refresh_token: Optional[str]
    token_type: Optional[str] = "bearer"


class UserResponseSchema(BaseModel):
    id: Optional[int]
    first_name: Optional[str]
    username: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class MessageSchema(BaseModel):
    status: bool
    message: str
    user: Optional[UserResponseSchema] = None
