import os
from os.path import join
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

Base_dir = Path(__file__).parent.parent
Env_path = join(Base_dir, '.env')
load_dotenv(Env_path)

SQLALCHEMY_DATABASE_URL = os.getenv('DB_URL')

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
