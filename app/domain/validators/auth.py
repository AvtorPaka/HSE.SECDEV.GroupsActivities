from email_validator import EmailNotValidError, validate_email

from app.domain.exceptions.domain import ValidationError
from app.domain.models.auth import UserLoginModel, UserRegisterModel


class UserRegisterModelValidator:
    def validate(self, model: UserRegisterModel):
        errors = []
        if not model.username or len(model.username.strip()) == 0:
            errors.append("Username is required")
        elif len(model.username) > 100:
            errors.append("Username must be less than 100 characters")

        if not model.email or len(model.email.strip()) == 0:
            errors.append("Email is required")
        else:
            try:
                validate_email(model.email, check_deliverability=False)
            except EmailNotValidError as e:
                errors.append(str(e))

        if not model.password:
            errors.append("Password is required")
        elif len(model.password) < 6:
            errors.append("Password must be at least 6 characters")

        if errors:
            from app.domain.exceptions.domain import BadRequestException

            raise BadRequestException("Validation failed", ValidationError(errors))


class UserLoginModelValidator:
    def validate(self, model: UserLoginModel):
        errors = []
        if not model.email or len(model.email.strip()) == 0:
            errors.append("Email is required")
        if not model.password:
            errors.append("Password is required")
        if errors:
            from app.domain.exceptions.domain import BadRequestException

            raise BadRequestException("Validation failed", ValidationError(errors))
