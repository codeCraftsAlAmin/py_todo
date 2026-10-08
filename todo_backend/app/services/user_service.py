from fastapi_pagination import Page

from ..config.exceptions import UserAlreadyExistsError, UserNotFoundError
from ..config.security import hash_password
from ..models.users_model import User
from ..repositories.user_repository import UserRepository
from ..schemas.users_schema import UserCreate


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def create_user(self, user_data: UserCreate) -> User:

        user_exist = self.user_repo.get_by_email(user_data.email)

        if user_exist:
            raise UserAlreadyExistsError(email=user_data.email)

        hashed_pw = hash_password(user_data.password)

        user_dic = user_data.model_dump(exclude={"password"})
        user_dic["hashed_password"] = hashed_pw

        db_user = User(**user_dic)
        return self.user_repo.create(user=db_user)

    def read_user(self) -> Page[User]:
        return self.user_repo.read()

    def get_user_by_id(self, id: int) -> User:
        user = self.user_repo.get_by_id(id=id)
        if user is None:
            raise UserNotFoundError(id=id)

        return user
