class DomainException(Exception):
    pass


class ValidationError(Exception):
    def __init__(self, errors: list):
        self.errors = errors

    def __str__(self):
        return ", ".join(self.errors)


class BadRequestException(DomainException):
    def __init__(self, message: str, validation_error: ValidationError = None):
        super().__init__(message)
        self.details = validation_error.errors if validation_error else None


class UserException(DomainException):
    pass


class UserAlreadyExistsException(UserException):
    def __init__(self, message: str, email: str, inner_exception: Exception = None):
        super().__init__(message)
        self.email = email
        self.inner_exception = inner_exception


class UserNotFoundException(UserException):
    def __init__(self, message: str, invalid_email: str = None, inner_exception: Exception = None):
        super().__init__(message)
        self.invalid_email = invalid_email
        self.inner_exception = inner_exception


class AuthUserNotFoundException(UserException):
    def __init__(self, message: str, invalid_email: str = None, inner_exception: Exception = None):
        super().__init__(message)
        self.invalid_email = invalid_email
        self.inner_exception = inner_exception


class InvalidUserCredentialsException(UserException):
    def __init__(
        self, message: str, email: str, invalid_password: str, inner_exception: Exception = None
    ):
        super().__init__(message)
        self.email = email
        self.invalid_password = invalid_password
        self.inner_exception = inner_exception


class UserUnauthenticatedException(UserException):
    def __init__(self, message: str, reason: str, inner_exception: Exception = None):
        super().__init__(message)
        self.reason = reason
        self.inner_exception = inner_exception
