import logging
from typing import Dict, Type

from fastapi import Request
from fastapi.responses import JSONResponse

from app.domain.exceptions.domain import (
    AuthUserNotFoundException,
    BadRequestException,
    DomainException,
    InvalidUserCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
    UserUnauthenticatedException,
)

from .error_responses import ApiError, create_error_response

logger = logging.getLogger(__name__)


class ExceptionHandler:
    def __init__(self):
        self._logger = logger
        self.exception_map: Dict[Type[DomainException], (int, str)] = {
            UserUnauthenticatedException: (401, "unauthorized"),
            InvalidUserCredentialsException: (200, "invalid_credentials"),
            AuthUserNotFoundException: (200, "invalid_credentials"),
            UserNotFoundException: (404, "user_not_found"),
            UserAlreadyExistsException: (202, "check_provided_email"),
            BadRequestException: (400, "bad_request"),
        }

    async def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        if isinstance(exc, DomainException):
            self._logger.info(f"Handled domain exception '{type(exc).__name__}': {exc}")

            status_code, error_code = self.exception_map.get(type(exc), (400, "bad_request"))

            details = getattr(exc, "details", None)

            api_error = ApiError(
                status_code=status_code, message=str(exc), code=error_code, details=details
            )
            return create_error_response(api_error)

        else:
            self._logger.error(
                f"An internal server error occurred due to exception '{type(exc).__name__}'",
                exc_info=True,
            )

            api_error = ApiError(
                status_code=500, message="Internal server error.", code="internal_error"
            )
            return create_error_response(api_error)
