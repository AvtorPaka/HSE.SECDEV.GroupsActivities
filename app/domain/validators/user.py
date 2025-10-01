from email_validator import EmailNotValidError, validate_email

from app.domain.exceptions.domain import BadRequestException, ValidationError
from app.domain.models.user import ChangeUserEmailModel, ChangeUserPasswordModel


class ChangeUserPasswordValidator:
    def validate(self, model: ChangeUserPasswordModel):
        errors = []

        if not model.new_password:
            errors.append("New password is required")
        elif len(model.new_password) < 6:
            errors.append("New password must be at least 6 characters")

        if errors:
            raise BadRequestException("Validation failed", ValidationError(errors))


class ChangeUserEmailValidator:
    def validate(self, model: ChangeUserEmailModel):
        errors = []

        if model.new_email == model.user.email:
            errors.append("New email must be different from current.")
        elif not model.new_email or len(model.new_email.strip()) == 0:
            errors.append("Email is required")
        else:
            try:
                validate_email(model.new_email, check_deliverability=False)
            except EmailNotValidError as e:
                errors.append(str(e))

        if errors:
            raise BadRequestException("Validation failed", ValidationError(errors))
