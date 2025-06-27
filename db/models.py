import asyncio
from enum import Enum
from sqlalchemy import Text, String, Enum as SQLEnum, DateTime
from sqlmodel import Field, SQLModel, Relationship

from db import engine
from db.config import CreatedModel


class StatusType(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Category(CreatedModel, table=True):
    __tablename__ = "categories"
    name: str = Field(sa_type=String)
    color: str = Field(sa_type=String)
    icon: str = Field(sa_type=String)
    tasks: list["Task"] = Relationship(back_populates="category")


class Task(CreatedModel, table=True):
    title: str = Field(sa_type=String)
    description: str = Field(sa_type=Text, nullable=True)
    category_id: int = Field(foreign_key="categories.id")
    status: str = Field(default=StatusType.NEW, sa_type=SQLEnum(StatusType, name='status'))
    priority: str = Field(sa_type=String)
    due_date: str = Field(sa_type=DateTime, nullable=True)
    category: "Category" = Relationship(back_populates="tasks")



class User(CreatedModel, table=True):
    first_name: str = Field(sa_type=String)
    username: str = Field(sa_type=String,unique=True)
    password: str = Field(sa_type=String)



async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


metadata = SQLModel.metadata

if __name__ == "__main__":
    asyncio.run(create_db_and_tables())
