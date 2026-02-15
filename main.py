import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# import bcrypt
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer

from admin.app import admin
from apps import main_router
from db import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    # print(bcrypt.hashpw("3".encode(), salt=bcrypt.gensalt()))
    yield
    await engine.dispose()


app = FastAPI(title="User API", version="1.0.0", lifespan=lifespan, docs_url="/docs", redoc_url="/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.include_router(main_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="My Super API",
        version="1.0.0",
        description="JWT Authentication bilan himoyalangan API",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation.setdefault("security", []).append({"BearerAuth": []})
    app.openapi_schema = openapi_schema
    return app.openapi_schema


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/")
app.openapi = custom_openapi
admin.mount_to(app)
