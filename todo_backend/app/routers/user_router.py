from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_pagination import Page, Params

from ..config.dependencies import SessionDep
from ..config.security import create_access_token, create_refresh_token
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

router = APIRouter(prefix="/api/users", tags=["users"])

ParamsDep: TypeAlias = Annotated[Params, Depends()]
FormDep: TypeAlias = Annotated[OAuth2PasswordRequestForm, Depends()]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# create user
@router.post(
    "/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(user: UserCreate, db: SessionDep):

    user_repo = UserRepository(db)

    create_user_service = user_service.UserService(user_repo)
    return await create_user_service.create_user(user)


# login user
@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_user(form_data: FormDep, db: SessionDep):
    user_repo = UserRepository(db)

    create_login_service = user_service.UserService(user_repo)
    login_payload = UserLogin(email=form_data.username, password=form_data.password)

    user = await create_login_service.login_user(login_payload)

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "id": user.id,
        "email": user.email,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


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
async def delete_user(id: int, db: SessionDep):
    user_repo = UserRepository(db)

    delete_user_service = user_service.UserService(user_repo)
    await delete_user_service.delete_user(id)
    return {"message": "User deleted successfully!"}


# update user
@router.patch(
    "/{id}/update-profile", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def update_user(id: int, user: UserUpdate, db: SessionDep):
    user_repo = UserRepository(db)
    update_user_service = user_service.UserService(user_repo)

    return await update_user_service.update_user_info(id=id, user_data=user)


# change password
@router.patch("/{id}/change-password", status_code=status.HTTP_200_OK)
async def change_password(id: int, password: UserChangePassword, db: SessionDep):
    user_repo = UserRepository(db)

    change_password_service = await user_service.UserService(user_repo)
    await change_password_service.change_password(id=id, passwords=password)
    return {"message": "Your password changed successfully!"}
