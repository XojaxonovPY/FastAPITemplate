from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from db import engine

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, autoflush=False
)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
