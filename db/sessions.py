from collections.abc import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from core.settings import Settings
from db.exceptions import DatabaseException, logger

SQLALCHEMY_DATABASE_URL = Settings.DB_URL

engine: AsyncEngine = create_async_engine(
    Settings.DB_URL, echo=False, future=True
)
# pool_size=20, max_overflow=10, pool_pre_ping=True

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, autoflush=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            logger.error(e)
            raise DatabaseException(message="Base error", code=503)
        finally:
            await session.close()
