from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer

from apps import tasks, login_register

app = FastAPI(title="User API")

app.include_router(tasks, prefix="/tasks", tags=["tasks"])
app.include_router(login_register, prefix="/login", tags=["login"])


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        description="My API with JWT Auth",
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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token/")

app.openapi = custom_openapi


import bcrypt

print(bcrypt.hashpw("3".encode(), salt=bcrypt.gensalt()))