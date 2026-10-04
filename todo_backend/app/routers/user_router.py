from fastapi import APIRouter, HTTPException, status

from ..config.dependencies import SessionDep
from ..models.users_model import User
from ..schemas.users_schema import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])

# create user
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: SessionDep):

    user_exist = db.query(User).filter(User.email == user.email).first()

    if user_exist:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = User(**user.model_dump())

    db.add(user_data)
    db.commit()
    db.refresh(user_data)

    return user_data

# get users
@router.get("/", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def read_users(db: SessionDep, skip: int = 0, limit: int = 100):
    users = db.query(User).offset(skip).limit(limit).all()
    return users
