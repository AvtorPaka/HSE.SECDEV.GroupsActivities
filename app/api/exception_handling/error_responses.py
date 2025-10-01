from typing import List, Optional

from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ApiErrorModel(BaseModel):
    code: str
    message: str
    details: Optional[List[str]] = None


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
    error_model = ApiErrorModel(
        code=api_error.code, message=api_error.message, details=api_error.details
    )
    return JSONResponse(
        status_code=api_error.status_code,
        content=ApiErrorResponse(error=error_model).model_dump(exclude_none=True),
    )
