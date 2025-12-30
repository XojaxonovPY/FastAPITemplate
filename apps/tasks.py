from typing import Optional

from fastapi import APIRouter
from starlette import status

from apps.depends import SessionDep
from db.models import User
from instruments.forms import UserForm

tasks = APIRouter()


@tasks.get("/users/list", response_model=list[User], status_code=status.HTTP_200_OK)
async def users_list(session: SessionDep) -> list[User]:
    users = await User.all_(session)
    return users


@tasks.get('/users/{username}', response_model=Optional[User], status_code=status.HTTP_200_OK)
async def get_user(session: SessionDep, username: str) -> Optional[User]:
    user = await User.get(session, username=username)
    return user


@tasks.get('/user/{first_name}', response_model=list[User], status_code=status.HTTP_200_OK)
async def get_user(session: SessionDep, first_name: str) -> list[Optional[User]]:
    user = await User.filter(session, User.first_name < first_name)
    return user


@tasks.patch('user/{pk}', response_model=User, status_code=status.HTTP_200_OK)
async def update_user(session: SessionDep, pk: int, user_data: UserForm) -> User:
    user = await User.update(session, pk, **user_data.model_dump(exclude_unset=True))
    return user
