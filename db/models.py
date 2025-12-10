import asyncio

from sqlalchemy import String, Column
from sqlmodel import Field, SQLModel

from db import engine
from db.config import Model


class User(Model, table=True):
    first_name: str = Field(sa_column=Column(String(length=50)))
    username: str = Field(sa_column=Column(String(length=50), unique=True))
    password: str = Field(sa_column=Column(String(length=200)))


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


metadata = SQLModel.metadata

if __name__ == "__main__":
    asyncio.run(create_db_and_tables())
