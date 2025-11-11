from typing import List, Optional
from uuid import uuid4

from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ApiErrorModel(BaseModel):
    title: str
    status: str
    details: Optional[List[str]] = None
    correlation_id: str


class ApiErrorResponse(BaseModel):
    error: ApiErrorModel


class ApiError:
    def __init__(
        self, status_code: int, code: str, message: str, details: Optional[List[str]] = None
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def create_error_response(api_error: ApiError) -> JSONResponse:
    cid = str(uuid4())
    error_model = ApiErrorModel(
        status=api_error.code,
        title=api_error.message,
        details=api_error.details,
        correlation_id=cid,
    )
    return JSONResponse(
        status_code=api_error.status_code,
        content=ApiErrorResponse(error=error_model).model_dump(exclude_none=True),
    )
