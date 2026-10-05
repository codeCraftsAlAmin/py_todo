from ..config.dependencies import SessionDep
from ..models.users_model import User


class UserRepository:
    def __init__(self, db: SessionDep):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user: User) -> User:
        user_data = User(**user.model_dump())

        self.db.add(user_data)
        self.db.commit()
        self.db.refresh(user_data)

        return user_data

    def read(self, skip=0, limit=100) -> list[User]:
        user = self.db.query(User).offset(skip).limit(limit).all()
        return user
