from ..config.dependencies import SessionDep
from ..models.users_model import User
from ..schemas.users_schema import UserCreate


class UserRepository:
    def __init__(self, db: SessionDep):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user: UserCreate) -> User:
        user_data = User(**user.model_dump())

        self.db.add(user_data)
        self.db.commit()
        self.db.refresh(user_data)

        return user_data
