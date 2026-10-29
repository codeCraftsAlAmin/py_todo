from fastapi_pagination import Page, Params
from loguru import logger
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.users_model import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create(self, user: User) -> User:
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create user. Error: {e}")
            raise

    async def read(self, params: Params) -> Page[User]:
        try:
            count_stmt = select(func.count()).select_from(User)
            total_count = await self.db.scalar(count_stmt)

            if total_count is None:
                total_count = 0

            offset = (params.page - 1) * params.size

            smt = select(User).offset(offset).limit(params.size)
            result = await self.db.execute(smt)
            items = result.scalars().all()

            return Page.create(items=items, total=total_count, params=params)

        except Exception as e:
            logger.error(f"Something went wrong, Error: {e}")
            raise

    async def get_by_id(self, id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == id))
        return result.scalars().first()

    async def delete(self, user_data: User):
        try:
            await self.db.delete(user_data)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete user. Error: {e}")
            raise

    async def update(self, user_data: User) -> User:
        try:
            await self.db.commit()
            await self.db.refresh(user_data)
            return user_data
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update user. Error: {e}")
            raise
