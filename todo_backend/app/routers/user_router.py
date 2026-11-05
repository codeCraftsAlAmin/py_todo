from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page, Params

from ..config.dependencies import SessionDep
from ..config.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    regenerate_access_token,
)
from ..models.users_model import User
from ..repositories.user_repository import UserRepository
from ..schemas.users_schema import (
    TokenResponse,
    UserChangePassword,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from ..services import user_service

router = APIRouter(prefix="/api/auth/users", tags=["Users"])

ParamsDep: TypeAlias = Annotated[Params, Depends()]
FormDep: TypeAlias = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser: TypeAlias = Annotated[User, Depends(get_current_user)]
TokenData: TypeAlias = Annotated[dict, Depends(regenerate_access_token)]


# create user
@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(user: UserCreate, db: SessionDep):

    user_repo = UserRepository(db)

    create_user_service = user_service.UserService(user_repo)
    return await create_user_service.create_user(user)


# login user
@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_user(form_data: FormDep, response: Response, db: SessionDep):
    user_repo = UserRepository(db)

    create_login_service = user_service.UserService(user_repo)
    login_payload = UserLogin(email=form_data.username, password=form_data.password)

    user = await create_login_service.login_user(login_payload)

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # stay hide from js
        secure=False,  # will be True in production
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7ds in sec
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # stay hide from js
        secure=False,  # will be True in production(HTTPS)
        samesite="lax",
        max_age=15 * 60,  # 15m in sec
    )

    return {"message": "Login successful", "id": user.id, "email": user.email}


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
async def get_user_by_id(id: int, db: SessionDep):
    user_repo = UserRepository(db)

    get_user_service = user_service.UserService(user_repo)

    return await get_user_service.get_user_by_id(id)


# delete user
@router.delete("/{id}/delete-user", status_code=status.HTTP_200_OK)
async def delete_user(db: SessionDep, current_user: CurrentUser):
    user_repo = UserRepository(db)

    delete_user_service = user_service.UserService(user_repo)
    await delete_user_service.delete_user(user=current_user)
    return {"message": "User deleted successfully!"}


# update user
@router.patch(
    "/{id}/update-profile", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def update_user(user: UserUpdate, db: SessionDep, current_user: CurrentUser):
    user_repo = UserRepository(db)
    update_user_service = user_service.UserService(user_repo)

    return await update_user_service.update_user_info(
        id=current_user.id, user_data=user
    )


# change password
@router.patch("/{id}/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password: UserChangePassword, db: SessionDep, current_user: CurrentUser
):
    user_repo = UserRepository(db)

    change_password_service = user_service.UserService(user_repo)
    await change_password_service.change_password(
        id=current_user.id, passwords=password
    )
    return {"message": "Your password changed successfully!"}


# refresh token
@router.post("/refresh-token", status_code=status.HTTP_200_OK)
async def refresh_token(response: Response, token_data: TokenData):
    new_access_token = token_data.get("access_token")

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,  # stay hide from js
        secure=False,  # will be True in production(HTTPS)
        samesite="lax",
        max_age=15 * 60,  # 15m in sec
    )

    return {
        "message": "Access token refreshed successfully",
    }
