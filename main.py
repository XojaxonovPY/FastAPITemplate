import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator, cast, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.middleware.sessions import SessionMiddleware

from admin.app import admin
from apps import main_router, exception_handler
from db.config import Base
from db.engine import engine


# ==========================================
# 1. LIFESPAN (Ilova hayotiy sikli)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Fast API",
    version="0.142.2",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    cast(Any, CORSMiddleware),
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Session Middleware
app.add_middleware(
    cast(Any, SessionMiddleware),
    secret_key="maxfiy_kalitingiz",
    max_age=14 * 24 * 60 * 60,
    same_site="lax",
    https_only=False,
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


app.include_router(main_router)
admin.mount_to(app)
app.openapi = custom_openapi
exception_handler(app)
