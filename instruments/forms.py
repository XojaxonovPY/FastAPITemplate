import datetime
from typing import Union

from pydantic import BaseModel, Field, validator, field_validator, ValidationError

from db.models import StatusType, User
from instruments.login import get_password_hash


class CategoryForm(BaseModel):
    name: str = Field(min_length=3)
    color: str = Field(min_length=3)
    icon: str = Field(min_length=3)

    @field_validator('icon')
    @classmethod
    def validate_icon(cls, value):
        if value.startswith('http'):
            return value
        else:
            raise ValueError('its not icon')


class TaskForm(BaseModel):
    title: str
    description: str
    category_id: int
    priority: Union[str, None] = None
    due_date: Union[datetime.datetime, None] = None


class TaskUpdateForm(BaseModel):
    title: str
    status: StatusType
    priority: str


class LoginForm(BaseModel):
    username: str = None
    password: str = None


class RegisterForm(BaseModel):
    first_name: str = None
    username: str = None
    password: str = None

    async def save(self, session):
        first_name = self.first_name
        username = self.username
        password = await get_password_hash(self.password)
        user = User(first_name=first_name, username=username, password=password)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user



class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    class Config:
        orm_mode = True