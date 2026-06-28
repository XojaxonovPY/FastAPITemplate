from typing import Annotated, TypeAlias

from fastapi import APIRouter, HTTPException, status, Body
from starlette.responses import JSONResponse

from apps.depends import SessionDep, UserSession
from db.models import User
from schemas import RegisterSchema, TokenResponseSchema, LoginSchema, UserResponseSchema
from services.login import (
    get_password_hash,
    verify_password,
    get_user,
    create_access_token,
    create_refresh_token,
    verify_token
)

router = APIRouter()

BodyStr: TypeAlias = Annotated[str, Body(embed=True)]


@router.post("/user/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def user_create(session: SessionDep, user: RegisterSchema):
    hashed_password = await get_password_hash(user.password)
    user_data = user.model_dump(exclude_unset=True)
    user_data["password"] = hashed_password
    async with session.begin():
        new_user = await User.create(session, **user_data)
    return new_user


# ==========================================
# 2. TIZIMGA KIRISH (LOGIN)
# ==========================================
@router.post("/login", response_model=TokenResponseSchema)
async def login(session: SessionDep, data: LoginSchema) -> JSONResponse:
    user = await get_user(session, username=data.username)
    if not user or not await verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username yoki parol noto'g'ri"
        )

    access_token = await create_access_token(subject=user.id)
    refresh_token_ = await create_refresh_token(subject=user.id)
    return JSONResponse({
        "access_token": access_token,
        "refresh_token": refresh_token_,
        "token_type": "bearer"
    })


@router.post("/refresh", response_model=TokenResponseSchema)
async def refresh_token(refresh_token_: BodyStr):
    payload = await verify_token(refresh_token_)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yaroqsiz yoki muddati o'tgan refresh token"
        )

    token_subject = payload["sub"]
    new_access_token = await create_access_token(subject=token_subject)
    new_refresh_token = await create_refresh_token(subject=token_subject)

    return JSONResponse({
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    })


# ==========================================
# 4. JORIY FOYDALANUVCHI (ME)
# ==========================================
@router.get("/users/me", response_model=UserResponseSchema, status_code=status.HTTP_200_OK)
async def read_users_me(current_user: UserSession):
    return current_user
