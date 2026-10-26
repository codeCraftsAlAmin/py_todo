from fastapi_pagination import Page, Params

from ..config.exceptions import (
    PasswordDidntMatch,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from ..config.security import hash_password, verify_password
from ..models.users_model import User
from ..repositories.user_repository import UserRepository
from ..schemas.users_schema import UserChangePassword, UserCreate, UserLogin, UserUpdate


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create_user(self, user_data: UserCreate) -> User:

        user_exist = await self.user_repo.get_by_email(user_data.email)

        if user_exist:
            raise UserAlreadyExistsError(email=user_data.email)

        hashed_pw = hash_password(user_data.password)

        user_dic = user_data.model_dump(exclude={"password"})
        user_dic["hashed_password"] = hashed_pw

        db_user = User(**user_dic)
        return await self.user_repo.create(user=db_user)

    async def login_user(self, user_data: UserLogin) -> User:
        user = await self.user_repo.get_by_email(email=user_data.email)

        if user is None:
            raise UserNotFoundError(email=user_data.email)

        is_valid_pass = verify_password(
            plain_password=user_data.password, hashed_password=user.hashed_password
        )

        if is_valid_pass is not True:
            raise PasswordDidntMatch()
        return user

    async def read_user(self, params: Params) -> Page[User]:
        return await self.user_repo.read(params)

    async def get_user_by_id(self, id: int) -> User:
        user = await self.user_repo.get_by_id(id=id)
        if user is None:
            raise UserNotFoundError(id=id)

        return user

    async def delete_user(self, user: User):
        # user = await self.user_repo.get_by_id(id=id)
        await self.user_repo.delete(user_data=user)

    async def update_user_info(self, id: int, user_data: UserUpdate) -> User:
        user = await self.user_repo.get_by_id(id)

        updated_data = user_data.model_dump(exclude_unset=True)

        for key, value in updated_data.items():
            setattr(user, key, value)

        return await self.user_repo.update(user_data=user)

    async def change_password(self, id: int, passwords: UserChangePassword):
        user = await self.user_repo.get_by_id(id=id)

        is_password_correct = verify_password(
            plain_password=passwords.old_password, hashed_password=user.hashed_password
        )

        if not is_password_correct:
            raise PasswordDidntMatch()

        hash_new_pass = hash_password(password=passwords.new_password)

        # update the new pass in db
        user.hashed_password = hash_new_pass

        return await self.user_repo.update(user_data=user)
