from typing import Optional

from fastapi import APIRouter, status, Response

from apps.depends import SessionDep
from db.models import User
from schemas import UserSchema, UserResponseSchema

router = APIRouter()


@router.get("/users/list", response_model=list[Optional[UserResponseSchema]], status_code=status.HTTP_200_OK)
async def users_list(session: SessionDep) -> list[Optional[UserResponseSchema]]:
    users = await User.all_(session, [User.id.asc()])
    return users


@router.get('/users/', response_model=Optional[UserResponseSchema], status_code=status.HTTP_200_OK)
async def get_user(session: SessionDep, username: str) -> Optional[UserResponseSchema]:
    user = await User.get(session, username=username)
    print(type(User.first_name))
    return user


@router.get('/user/', response_model=list[Optional[UserResponseSchema]], status_code=status.HTTP_200_OK)
async def get_user(session: SessionDep, first_name: Optional[str] = None) -> list[Optional[UserResponseSchema]]:
    user = await User.filter(session, User.first_name == first_name, order_by=[User.id.desc()])
    return user


@router.patch('/user/{pk}', response_model=UserResponseSchema, status_code=status.HTTP_200_OK)
async def update_user(session: SessionDep, pk: int, user_data: UserSchema) -> User:
    user = await User.update(session, {"id": pk}, **user_data.model_dump(exclude_unset=True))
    return user


@router.delete('/user/{pk}', status_code=status.HTTP_205_RESET_CONTENT)
async def delete_user(session: SessionDep, pk: int) -> Response:
    await User.delete(session, {"id": pk})
    return Response(status_code=status.HTTP_205_RESET_CONTENT)
