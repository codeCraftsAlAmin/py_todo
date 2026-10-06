from fastapi import APIRouter, status
from fastapi_pagination import Page

from ..config.dependencies import SessionDep

# from ..models.users_model import User
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
