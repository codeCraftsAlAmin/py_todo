from fastapi import APIRouter, status
from fastapi_pagination import Page

from ..config.dependencies import SessionDep
from ..repositories.user_repository import UserRepository
from ..schemas.users_schema import UserCreate, UserResponse
from ..services import user_service

router = APIRouter(prefix="/users", tags=["users"])


# create user
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: SessionDep):

    user_repo = UserRepository(db)

    create_user_service = user_service.UserService(user_repo)
    return create_user_service.create_user(user)


# get users
@router.get("/", response_model=Page[UserResponse], status_code=status.HTTP_200_OK)
def read_users(db: SessionDep):

    user_repo = UserRepository(db)

    read_user_data = user_service.UserService(user_repo)
    return read_user_data.read_user()


# get user by id
@router.get("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(id: int, db: SessionDep):
    user_repo = UserRepository(db)

    user_data = user_service.UserService(user_repo)

    return user_data.get_user_by_id(id)


# delete user
@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_user(id: int, db: SessionDep):
    user_repo = UserRepository(db)

    delete_data = user_service.UserService(user_repo)
    delete_data.delete_user(id)
    return {"message": "User deleted successfully"}
