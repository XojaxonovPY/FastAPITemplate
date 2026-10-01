import asyncio
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from db.sessions import get_session

SECRET_KEY = "629c7d363ffa1562c4fbe09742653d9ccf149621cb662bf69746a6e6476eff63"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 5
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/")


# ==========================================
# 1. PAROLLAR BILAN ISHLASH (Xavfsiz Bcrypt)
# ==========================================

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Parolni to'g'ridan-to'g'ri bcrypt orqali tekshirish"""
    return await asyncio.to_thread(
        bcrypt.checkpw,
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


async def get_password_hash(password: str) -> str:
    """Xavfsiz salt bilan parolni xeshirlash"""

    def _hash():
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    return await asyncio.to_thread(_hash)


# ==========================================
# 2. TOKEN GENERATSIYASI (PyJWT + UTC)
# ==========================================

def create_token(payload: dict[str, str], expires_delta: timedelta) -> str:
    """Token yaratish uchun markazlashgan xavfsiz funksiya"""
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(subject: str) -> str:
    """
    subject: Foydalanuvchining ID si, emaili yoki username bo'lishi mumkin (Dinamik)
    """
    delta = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    return create_token({"sub": str(subject), "type": "access"}, delta)


def create_refresh_token(subject: str) -> str:
    delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token({"sub": str(subject), "type": "refresh"}, delta)


# ==========================================
# 3. TOKEN VALIDATSIYASI VA DINAMIK USER FILTRI
# ==========================================

def verify_token(token: str) -> dict:
    """Tokenni tekshirish va dekod qilish"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return {}


async def get_current_user(session: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)) -> User:
    """Foydalanuvchini token turiga qarab dinamik aniqlash funksiyasi"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token)
    if not payload or payload.get("type") != "access":
        raise credentials_exception

    subject: str | None = payload.get("sub")
    if not subject:
        raise credentials_exception

    user = await User.get(session, User.id == int(subject))
    if user is None:
        raise credentials_exception

    return user
