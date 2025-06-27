import asyncio

from sqlalchemy import Text, String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Field, SQLModel

SQLALCHEMY_DATABASE_URL = 'postgresql+asyncpg://postgres:1@localhost:5432/test'

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)






