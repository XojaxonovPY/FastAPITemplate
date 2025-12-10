from sqlalchemy.ext.asyncio import create_async_engine

from utils.settings import Settings

SQLALCHEMY_DATABASE_URL = Settings.DB_URL

engine = create_async_engine(Settings.DB_URL, echo=False, future=True)
