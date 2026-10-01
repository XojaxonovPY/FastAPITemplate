from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from db.engine import engine
from db.exceptions import DatabaseException, logger

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, autoflush=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(e)
            raise DatabaseException(message="Base error", code=502)
        finally:
            await session.close()
