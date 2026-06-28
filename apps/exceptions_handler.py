from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from db.exceptions import DatabaseException


def exception_handler(app: FastAPI):
    @app.exception_handler(DatabaseException)
    def database_exceptions(request: Request, exc: DatabaseException):
        return JSONResponse(status_code=exc.code, content={'message': exc.message})
