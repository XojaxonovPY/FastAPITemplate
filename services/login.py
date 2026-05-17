import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional, Any

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from db.sessions import get_session

SECRET_KEY = "629c7d363ffa1562c4fbe09742653d9ccf149621cb662bf69746a6e6476eff63"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/")


# ==========================================
# 1. PAROLLAR BILAN ISHLASH (Xavfsiz Bcrypt)
# ==========================================

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Parolni to'g'ridan-to'g'ri bcrypt orqali tekshirish (SHA-256 aralashtirmasdan)"""

    def _verify():
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    return await asyncio.to_thread(_verify)


async def get_password_hash(password: str) -> str:
    """Xavfsiz salt bilan parolni xeshirlash"""

    def _hash():
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    return await asyncio.to_thread(_hash)


# ==========================================
# 2. TOKEN GENERATSIYASI (PyJWT + UTC)
# ==========================================

async def create_token(payload: dict, expires_delta: timedelta) -> str:
    """Token yaratish uchun markazlashgan xavfsiz funksiya"""
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return await asyncio.to_thread(jwt.encode, to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def create_access_token(subject: Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    subject: Foydalanuvchining ID si, emaili yoki username bo'lishi mumkin (Dinamik)
    """
    delta = expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return await create_token({"sub": str(subject), "type": "access"}, delta)


async def create_refresh_token(subject: Any) -> str:
    delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return await create_token({"sub": str(subject), "type": "refresh"}, delta)


# ==========================================
# 3. TOKEN VALIDATSIYASI VA DINAMIK USER FILTRI
# ==========================================

async def verify_token(token: str) -> dict | None:
    """Tokenni tekshirish va dekod qilish"""
    try:
        return await asyncio.to_thread(jwt.decode, token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None


async def get_current_user(session: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)) -> User:
    """Foydalanuvchini token turiga qarab dinamik aniqlash funksiyasi"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Muddati o'tgan yoki noto'g'ri token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = await verify_token(token)
    if not payload or payload.get("type") != "access":
        raise credentials_exception

    token_subject = payload.get("sub")
    if not token_subject:
        raise credentials_exception
    filter_query = {}

    if token_subject.isdigit():
        filter_query["id"] = int(token_subject)
    elif "@" in token_subject:
        filter_query["email"] = token_subject
    else:
        filter_query["username"] = token_subject

    user = await User.get(session, **filter_query)
    if user is None:
        raise credentials_exception

    return user


# ==========================================
# 4. JOZIRGI USERNI BERISH
# ==========================================

async def get_user(session: AsyncSession, **filter_) -> Optional[User]:
    result: User | None = await User.get(session, **filter_)
    return result
