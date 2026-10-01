from typing import Optional

from fastapi import APIRouter, status, Response, HTTPException

from apps.depends import SessionDep
from db.models import User
from schemas import UserResponseSchema, UserSchema, MessageSchema

router = APIRouter()


@router.get("/users/list/", response_model=list[Optional[UserResponseSchema]], status_code=status.HTTP_200_OK)
async def users_list(session: SessionDep) -> list[Optional[UserResponseSchema]]:
    users = await User.get_all(session, order_by=[User.id.asc()], fields=UserResponseSchema)
    return users


@router.get('/users/', response_model=Optional[UserResponseSchema], status_code=status.HTTP_200_OK)
async def get_user_by_username(session: SessionDep, username: str) -> Optional[UserResponseSchema]:
    user: User | None = await User.get(session, User.username == username, fields=UserResponseSchema)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get('/user/', response_model=list[Optional[UserResponseSchema]], status_code=status.HTTP_200_OK)
async def get_user_by_first_name(session: SessionDep, first_name: Optional[str] = None) -> list[
    Optional[UserResponseSchema]]:
    user = await User.get_all(
        session, User.first_name == first_name, order_by=[User.id.desc()],
        fields=UserResponseSchema
    )
    return user


@router.patch('/user/{pk}', response_model=MessageSchema, status_code=status.HTTP_200_OK)
async def update_user(session: SessionDep, pk: int, user_data: UserSchema) -> MessageSchema:
    count = await User.update(session, User.id == pk, **user_data.model_dump(exclude_unset=True))
    if count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return MessageSchema(status=True, message="User updated successfully")


@router.delete('/user/{pk}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(session: SessionDep, pk: int):
    count = await User.delete(session, User.id == pk)
    if count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
