import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.middleware import Middleware

from admin.app import admin
from apps import main_router
from db import engine


# ==========================================
# 1. LIFESPAN (Ilova hayotiy sikli)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    yield
    await engine.dispose()


middlewares = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]


app = FastAPI(
    title="User API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    middleware=middlewares
)


# ==========================================
# 3. HTTP CUSTOM MIDDLEWARE (Process Time)
# ==========================================
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f} sec"
    return response


app.include_router(main_router)
admin.mount_to(app)


# ==========================================
# 4. SWAGGER OPENAPI SECURITY OVERRIDE
# ==========================================
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
    public_paths = ["/login", "/user/register", "/docs", "/redoc", "/openapi.json"]

    for path, path_item in openapi_schema["paths"].items():
        if path not in public_paths:
            for operation in path_item.values():
                operation.setdefault("security", []).append({"BearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
