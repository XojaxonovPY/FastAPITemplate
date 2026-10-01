from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from starlette import status

from db.exceptions import DatabaseException


def exception_handler(app: FastAPI):
    @app.exception_handler(DatabaseException)
    def database_exceptions(request: Request, exc: DatabaseException):
        return JSONResponse(status_code=exc.code, content={"status": False, 'message': exc.message})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = {}
        for err in exc.errors():
            field = err["loc"][-1]
            errors[field] = err["msg"]

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": False,
                "errors": errors
            }
        )

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers,
            content={
                "status": False,
                "message": exc.detail,
            },
        )
