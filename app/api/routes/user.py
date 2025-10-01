# app/api/routes/user.py

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_user_service
from app.api.dto.user import (
    UserChangeEmailRequest,
    UserChangeEmailResponse,
    UserChangePasswordRequest,
    UserChangePasswordResponse,
)
from app.domain.models.user import ChangeUserEmailModel, ChangeUserPasswordModel, UserModel
from app.domain.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/change-password", response_model=UserChangePasswordResponse)
async def change_current_user_password(
    request_data: UserChangePasswordRequest,
    current_user: UserModel = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    change_password_model = ChangeUserPasswordModel(
        user=current_user,
        current_password=request_data.current_password,
        new_password=request_data.new_password,
    )

    await user_service.change_user_password(change_password_model)

    return UserChangePasswordResponse()


@router.patch("/change-email", response_model=UserChangeEmailResponse)
async def change_current_user_email(
    request_data: UserChangeEmailRequest,
    current_user: UserModel = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    change_email_model = ChangeUserEmailModel(
        user=current_user,
        provided_password=request_data.password,
        new_email=request_data.new_email,
    )

    await user_service.change_user_email(change_email_model)

    return UserChangeEmailResponse()
