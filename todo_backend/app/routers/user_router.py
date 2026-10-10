from fastapi import APIRouter, status
from fastapi_pagination import Page

from ..config.dependencies import SessionDep
from ..repositories.user_repository import UserRepository
from ..schemas.users_schema import (
    UserChangePassword,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from ..services import user_service

router = APIRouter(prefix="/api/users", tags=["users"])


# create user
@router.post("/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: SessionDep):

    user_repo = UserRepository(db)

    create_user_service = user_service.UserService(user_repo)
    return create_user_service.create_user(user)


# get users
@router.get("/", response_model=Page[UserResponse], status_code=status.HTTP_200_OK)
def read_users(db: SessionDep):

    user_repo = UserRepository(db)

    read_user_service = user_service.UserService(user_repo)
    return read_user_service.read_user()


# get user by id
@router.get("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(id: int, db: SessionDep):
    user_repo = UserRepository(db)

    get_user_service = user_service.UserService(user_repo)

    return get_user_service.get_user_by_id(id)


# delete user
@router.delete("/{id}/delete-user", status_code=status.HTTP_200_OK)
def delete_user(id: int, db: SessionDep):
    user_repo = UserRepository(db)

    delete_user_service = user_service.UserService(user_repo)
    delete_user_service.delete_user(id)
    return {"message": "User deleted successfully!"}


# update user
@router.patch(
    "/{id}/update-profile", response_model=UserResponse, status_code=status.HTTP_200_OK
)
def update_user(id: int, user: UserUpdate, db: SessionDep):
    user_repo = UserRepository(db)
    update_user_service = user_service.UserService(user_repo)

    return update_user_service.update_user_info(id=id, user_data=user)


# change password
@router.patch("/{id}/change-password", status_code=status.HTTP_200_OK)
def change_password(id: int, password: UserChangePassword, db: SessionDep):
    user_repo = UserRepository(db)

    change_password_service = user_service.UserService(user_repo)
    change_password_service.change_password(id=id, passwords=password)
    return {"message": "Your password changed successfully!"}
