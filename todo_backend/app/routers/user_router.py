import uuid
from typing import Annotated, TypeAlias

import jwt
from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page, Params

from ..config.dependencies import SessionDep
from ..config.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    regenerate_access_token,
    remove_auth_cookies,
    set_auth_cookies,
)
from ..config.settings import setting
from ..models.users_model import User
from ..repositories.user_repository import UserRepository
from ..schemas.users_schema import (
    MessageResponse,
    ResendOTPRequest,
    TokenResponse,
    UserChangePassword,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    VerifyEmailRequest,
)
from ..services import user_service
from ..utils.rate_limiter import rate_limiter
from ..utils.token_service import revoke_all_devices, revoke_single_device

router = APIRouter(prefix="/api/auth/users", tags=["Users"])

ParamsDep: TypeAlias = Annotated[Params, Depends()]
FormDep: TypeAlias = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser: TypeAlias = Annotated[User, Depends(get_current_user)]
TokenData: TypeAlias = Annotated[dict, Depends(regenerate_access_token)]

AuthRateLimit = [Depends(rate_limiter(max_req=5, window_sec=300))]
LoginRateLimit = [Depends(rate_limiter(max_req=10, window_sec=300))]


# create user
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=AuthRateLimit,
)
async def create_user(
    user: UserCreate, background_tasks: BackgroundTasks, db: SessionDep
):

    user_repo = UserRepository(db)

    create_user_service = user_service.UserService(user_repo)
    return await create_user_service.create_user(user, background_tasks)


# login user
@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=LoginRateLimit,
    status_code=status.HTTP_200_OK,
)
async def login_user(form_data: FormDep, response: Response, db: SessionDep):
    user_repo = UserRepository(db)

    create_login_service = user_service.UserService(user_repo)
    login_payload = UserLogin(email=form_data.username, password=form_data.password)

    user = await create_login_service.login_user(login_payload)

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = await create_refresh_token({"sub": str(user.id)})

    set_auth_cookies(
        response=response, access_token=access_token, refresh_token=refresh_token
    )

    return {"message": "Login successful", "id": user.id, "email": user.email}


# verify_email
@router.post(
    "/verify-email",
    response_model=MessageResponse,
    dependencies=LoginRateLimit,
    status_code=status.HTTP_200_OK,
)
async def verify_email(payload: VerifyEmailRequest, db: SessionDep):
    user_repo = UserRepository(db)

    verify_user_otp = user_service.UserService(user_repo)
    return await verify_user_otp.verify_user_email(email=payload.email, otp=payload.otp)


# resend otp
@router.post(
    "/resend-otp",
    response_model=MessageResponse,
    dependencies=AuthRateLimit,
    status_code=status.HTTP_200_OK,
)
async def resend_otp(
    payload: ResendOTPRequest, background_tasks: BackgroundTasks, db: SessionDep
):
    user_repo = UserRepository(db)
    resend_otp_service = user_service.UserService(user_repo)
    return await resend_otp_service.resend_verification_otp(
        email=payload.email, background_tasks=background_tasks
    )


# logout from single device
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        try:
            payload = jwt.decode(
                refresh_token,
                setting.SECRET_KEY,
                algorithms=[setting.ALGORITHM],
                options={"verify_exp": False},
            )

            user_id = payload.get("sub")
            family_id = payload.get("fid")
            token_type = payload.get("type")

            if user_id and family_id and token_type == "refresh":
                uuid.UUID(str(user_id))
                uuid.UUID(str(family_id))
                await revoke_single_device(str(user_id), str(family_id))
        except (jwt.InvalidTokenError, ValueError):
            pass
    remove_auth_cookies(response=response)
    return {"message": "Logged out from this device successfully"}


# logout from all devices
@router.post("/logout-all", status_code=status.HTTP_200_OK)
async def logout_all_devices(
    request: Request, response: Response, current_user: CurrentUser
):
    await revoke_all_devices(user_id=str(current_user.id))
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            payload = jwt.decode(
                refresh_token,
                setting.SECRET_KEY,
                algorithms=[setting.ALGORITHM],
                options={"verify_exp": False},
            )
            family_id = payload.get("fid")
            if family_id:
                uuid.UUID(str(family_id))
                await revoke_single_device(str(current_user.id), str(family_id))
        except (jwt.InvalidTokenError, ValueError):
            pass

    remove_auth_cookies(response=response)
    return {"message": "Logged out from all devices successfully"}


# get my profile
@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_my_profile(current_user: CurrentUser):
    return current_user


# get users
@router.get("/", response_model=Page[UserResponse], status_code=status.HTTP_200_OK)
async def read_users(db: SessionDep, params: ParamsDep):

    user_repo = UserRepository(db)

    read_user_service = user_service.UserService(user_repo)
    return await read_user_service.read_user(params)


# get user by id
@router.get("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(id: uuid.UUID, db: SessionDep):
    user_repo = UserRepository(db)

    get_user_service = user_service.UserService(user_repo)

    return await get_user_service.get_user_by_id(id)


# delete user
@router.delete("/me/delete-user", status_code=status.HTTP_200_OK)
async def delete_user(db: SessionDep, current_user: CurrentUser):
    user_repo = UserRepository(db)

    delete_user_service = user_service.UserService(user_repo)
    await delete_user_service.delete_user(user=current_user)
    return {"message": "User deleted successfully!"}


# update user
@router.patch(
    "/me/update-profile", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def update_user(user: UserUpdate, db: SessionDep, current_user: CurrentUser):
    user_repo = UserRepository(db)
    update_user_service = user_service.UserService(user_repo)

    return await update_user_service.update_user_info(
        id=current_user.id, user_data=user
    )


# change password
@router.patch("/me/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password: UserChangePassword, db: SessionDep, current_user: CurrentUser
):
    user_repo = UserRepository(db)

    change_password_service = user_service.UserService(user_repo)
    await change_password_service.change_password(
        id=current_user.id, passwords=password
    )
    return {"message": "Your password changed successfully!"}


# refresh token & rotate access
@router.post("/refresh-token", status_code=status.HTTP_200_OK)
async def refresh_token(response: Response, token_data: TokenData):
    new_access_token = token_data.get("access_token")
    new_refresh_token = token_data.get("refresh_token")
    refresh_max_age = token_data.get("refresh_max_age")

    set_auth_cookies(
        response=response,
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        refresh_max_age=refresh_max_age,
    )

    return {
        "message": "Access token refreshed successfully",
    }
