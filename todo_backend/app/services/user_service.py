from fastapi_pagination import Page

from ..config.exceptions import UserAlreadyExistsError
from ..models.users_model import User
from ..repositories.user_repository import UserRepository
from ..schemas.users_schema import UserCreate


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def create_user(self, user: UserCreate) -> User:

        user_exist = self.user_repo.get_by_email(user.email)

        if user_exist:
            raise UserAlreadyExistsError(email=user.email)

        return self.user_repo.create(user=user)

    def read_user(self) -> Page[User]:
        return self.user_repo.read()
