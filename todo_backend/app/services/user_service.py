from fastapi import HTTPException, status

from ..config.dependencies import SessionDep
from ..models.users_model import User
from ..schemas.users_schema import UserCreate


class UserService:
    def __init__(self, db: SessionDep):
        self.db = db

    async def create_user(self, user: UserCreate) -> User:

        user_exist = self.db.query(User).filter(User.email == user.email).first()
        if user_exist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user_data = User(**user.model_dump())

        self.db.add(user_data)
        self.db.commit()
        self.db.refresh(user_data)

        return user_data
