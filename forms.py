import datetime
from typing import Union

from pydantic import BaseModel

from db.models import StatusType, User
from login import get_password_hash


class CategoryForm(BaseModel):
    name: str
    color: str
    icon: str


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
        password = get_password_hash(self.password)
        user = User(first_name=first_name, username=username, password=password)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
