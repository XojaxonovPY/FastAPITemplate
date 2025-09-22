# import json
# import os
# import sys
# from unittest.mock import patch
#
# import pytest
# import pytest_asyncio
# from httpx import AsyncClient, ASGITransport
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
#
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#
# from main import app
# from db.models import metadata
# from db.sessions import get_db
#
# DATABASE_URL = "sqlite+aiosqlite:///./test.db"
# engine_test = create_async_engine(DATABASE_URL, echo=True)
# TestSessionLocal = sessionmaker(bind=engine_test, class_=AsyncSession, expire_on_commit=False)
#
#
# async def override_get_session():
#     async with TestSessionLocal() as session:
#         yield session
#
#
# app.dependency_overrides[get_db] = override_get_session
#
#
# @pytest_asyncio.fixture(scope="module", autouse=True)
# async def setup_db():
#     async with engine_test.begin() as conn:
#         await conn.run_sync(metadata.create_all)
#
# async def login_user():
#     transport = ASGITransport(app=app)
#     async with AsyncClient(transport=transport, base_url="http://test") as client:
#         response = await client.post("/login/token", json={
#             "email": 'botir@gmail.com',
#             "password": "1"
#         })
#         assert 200 <= response.status_code <= 400, 'User not registered'
#         access_token = response.json().get('access_token')
#         return access_token

# test.py
