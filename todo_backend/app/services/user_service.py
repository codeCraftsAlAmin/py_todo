import uuid

from fastapi import BackgroundTasks
from fastapi_pagination import Page, Params

from ..config.exceptions import (
    DidntMatchVerifyOtp,
    EmailNotVerifiedError,
    NotAllowedToResendOtp,
    PasswordDidntMatch,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from ..config.security import hash_password, verify_password
from ..models.users_model import User
from ..repositories.user_repository import UserRepository
from ..schemas.users_schema import UserChangePassword, UserCreate, UserLogin, UserUpdate
from ..utils.email_service import send_verification_otp_email
from ..utils.otp_service import generate_otp, is_resend_allowed, save_otp, verify_otp


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create_user(
        self, user_data: UserCreate, background_tasks: BackgroundTasks
    ) -> User:

        user_exist = await self.user_repo.get_by_email(user_data.email)

        if user_exist:
            raise UserAlreadyExistsError(email=user_data.email)

        hashed_pw = hash_password(user_data.password)

        user_dic = user_data.model_dump(exclude={"password"})
        user_dic["hashed_password"] = hashed_pw

        db_user = User(**user_dic)
        created_user = await self.user_repo.create(user=db_user)

        otp = generate_otp()
        await save_otp(created_user.email, otp)
        background_tasks.add_task(send_verification_otp_email, created_user.email, otp)

        return created_user

    async def login_user(self, user_data: UserLogin) -> User:
        user = await self.user_repo.get_by_email(email=user_data.email)

        if user is None:
            raise UserNotFoundError(email=user_data.email)

        is_valid_pass = verify_password(
            plain_password=user_data.password, hashed_password=user.hashed_password
        )

        if is_valid_pass is not True:
            raise PasswordDidntMatch()

        if not user.is_verified:
            raise EmailNotVerifiedError()
        return user

    async def verify_user_email(self, email: str, otp: str) -> dict[str, str]:
        user = await self.user_repo.get_by_email(email=email)
        if user is None:
            raise UserNotFoundError(email=email)

        if user.is_verified:
            return {"message": "Email is already verified."}

        is_valid, message = await verify_otp(email=user.email, submitted_otp=otp)
        if not is_valid:
            raise DidntMatchVerifyOtp(message=message)

        user.is_verified = True
        await self.user_repo.update(user_data=user)
        return {"message": "Email verified successfully! You can now log in."}

    async def resend_verification_otp(
        self, email: str, background_tasks: BackgroundTasks
    ) -> dict[str, str]:
        user = await self.user_repo.get_by_email(email=email)
        if user is None:
            raise UserNotFoundError(email=email)

        if user.is_verified:
            return {"message": "Email is already verified."}

        is_allowed, remaining_seconds = await is_resend_allowed(email=user.email)
        if not is_allowed:
            raise NotAllowedToResendOtp(remaining_seconds=remaining_seconds)

        otp = generate_otp()
        await save_otp(email=user.email, otp=otp)
        background_tasks.add_task(send_verification_otp_email, user.email, otp)
        return {"message": "A new verification OTP has been sent to your email."}

    async def read_user(self, params: Params) -> Page[User]:
        return await self.user_repo.read(params)

    async def get_user_by_id(self, id: uuid.UUID) -> User:
        user = await self.user_repo.get_by_id(id=id)
        if user is None:
            raise UserNotFoundError(id=id)

        return user

    async def delete_user(self, user: User):
        # user = await self.user_repo.get_by_id(id=id)
        await self.user_repo.delete(user_data=user)

    async def update_user_info(self, id: uuid.UUID, user_data: UserUpdate) -> User:
        user = await self.user_repo.get_by_id(id)

        updated_data = user_data.model_dump(exclude_unset=True)

        for key, value in updated_data.items():
            setattr(user, key, value)

        return await self.user_repo.update(user_data=user)

    async def change_password(self, id: uuid.UUID, passwords: UserChangePassword):
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
