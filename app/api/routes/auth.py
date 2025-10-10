from fastapi import APIRouter, Depends, Request, Response

from app.api.dependencies import SESSION_COOKIE_KEY, get_auth_service
from app.api.dto.auth import (
    UserCheckAuthResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserLogoutResponse,
    UserRegisterRequest,
    UserRegisterResponse,
)
from app.domain.models.auth import UserLoginModel, UserRegisterModel
from app.domain.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserRegisterResponse)
async def user_register(
    request: UserRegisterRequest, auth_service: AuthService = Depends(get_auth_service)
):
    register_model = UserRegisterModel(
        username=request.username or "", email=request.email or "", password=request.password or ""
    )

    await auth_service.register_new_user(register_model)
    return UserRegisterResponse()


@router.post("/login", response_model=UserLoginResponse)
async def user_login(
    request: UserLoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    login_model = UserLoginModel(email=request.email or "", password=request.password or "")
    set_cookie_model = await auth_service.login_user(login_model)

    response.set_cookie(
        key=SESSION_COOKIE_KEY,
        value=set_cookie_model.session.id,
        expires=set_cookie_model.session.expiration_date,
        httponly=True,
        # secure=True
        # samesite="lax"
    )

    return UserLoginResponse(
        id=set_cookie_model.user.id,
        email=set_cookie_model.user.email,
        username=set_cookie_model.user.username,
    )


@router.get("/check", response_model=UserCheckAuthResponse)
async def user_check_auth(request: Request, auth_service: AuthService = Depends(get_auth_service)):
    session_id = request.cookies.get(SESSION_COOKIE_KEY)
    user_model = await auth_service.user_check_auth(session_id)

    return UserCheckAuthResponse(
        id=user_model.id, email=user_model.email, username=user_model.username
    )


@router.delete("/logout", response_model=UserLogoutResponse)
async def user_logout(
    request: Request, response: Response, auth_service: AuthService = Depends(get_auth_service)
):
    session_id = request.cookies.get(SESSION_COOKIE_KEY) or ""

    await auth_service.logout_user(session_id)
    response.delete_cookie(
        key=SESSION_COOKIE_KEY,
        httponly=True,
        # secure=True,
        # samesite="lax"
    )

    return UserLogoutResponse()
