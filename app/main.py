from fastapi import FastAPI, HTTPException, Request

from app.api.exception_handling import ApiError, ExceptionHandler, create_error_response
from app.api.routes import auth_router, user_router
from app.domain.exceptions.domain import DomainException
from app.logging_config import setup_logging

setup_logging()

app = FastAPI(title="SecDev StudyGroups", version="0.1.0")

exception_handler = ExceptionHandler()


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return await exception_handler.handle_exception(request, exc)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        detail = exc.detail if isinstance(exc.detail, str) else "http_error"
        api_error = ApiError(status_code=exc.status_code, message=detail, code="http_error")
        return create_error_response(api_error)
    return await exception_handler.handle_exception(request, exc)


app.include_router(auth_router)
app.include_router(user_router)


@app.get("/health")
def health():
    return {"status": "ok"}
