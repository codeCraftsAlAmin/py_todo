from fastapi import APIRouter, status

from ..config.dependencies import SessionDep
from ..models.users_model import User
from ..schemas.users_schema import UserCreate, UserResponse
from ..services import user_service

router = APIRouter(prefix="/users", tags=["users"])


# create user
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: SessionDep):
    create_user_service = user_service.UserService(db)
    return await create_user_service.create_user(user)


# get users
@router.get("/", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def read_users(db: SessionDep, skip: int = 0, limit: int = 100):
    users = db.query(User).offset(skip).limit(limit).all()
    return users
