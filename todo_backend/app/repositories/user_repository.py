from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from ..models.users_model import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def read(self) -> Page[User]:
        # user = self.db.query(User).offset(skip).limit(limit).all()
        user = paginate(self.db, self.db.query(User))
        return user

    def get_by_id(self, id: int) -> User | None:
        return self.db.query(User).filter(User.id == id).first()

    def delete(self, user_data: User):
        self.db.delete(user_data)
        self.db.commit()

    def update(self, user_data: User) -> User:
        self.db.commit()
        self.db.refresh(user_data)
        return user_data
