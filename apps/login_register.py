from typing import TypeAlias, Annotated

from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import JSONResponse

from apps.depends import SessionDep
from db.models import User
from instruments.login import create_refresh_token, verify_token, get_password_hash, UserSession
from instruments.login import get_user, create_access_token, verify_password
from schemas import RegisterSchema, TokenResponseSchema, LoginSchema, UserResponseSchema

router = APIRouter()

BodyStr: TypeAlias = Annotated[str, Body(embed=True)]


@router.post("/user/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def user_create(session: SessionDep, user: RegisterSchema) -> User:
    user.password = await get_password_hash(user.password)
    user = await User.create(session, **user.model_dump(exclude_unset=True))
    return user


@router.post("/login", response_model=TokenResponseSchema)
async def login(session: SessionDep, data: LoginSchema) -> JSONResponse:
    user = await get_user(session, username=data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    verify = await verify_password(data.password, user.password)
    if not user or not verify:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token: str = await create_access_token(data={"sub": user.username})
    refresh_token_: str = await create_refresh_token(data={"sub": user.username})
    return JSONResponse({"access_token": access_token, "refresh_token": refresh_token_, "token_type": "bearer"})


@router.post("/refresh", response_model=TokenResponseSchema)
async def refresh_token(refresh_token_: BodyStr) -> JSONResponse:
    payload = await verify_token(refresh_token_)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_data = {"sub": payload["sub"]}
    new_access_token: str = await create_access_token(user_data)
    new_refresh_token: str = await create_refresh_token(user_data)
    return JSONResponse({"access_token": new_access_token, "refresh_token": new_refresh_token})


@router.get("/users/me", response_model=UserResponseSchema, status_code=status.HTTP_200_OK)
async def read_users_me(current_user: UserSession) -> User:
    return current_user
