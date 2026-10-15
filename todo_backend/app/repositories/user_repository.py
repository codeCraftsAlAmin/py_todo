from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from loguru import logger
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

    async def read(self) -> Page[User]:
        # user = self.db.query(User).offset(skip).limit(limit).all()
        user = await paginate(self.db, self.db.select(User))
        return user

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
            logger.error(f"Failed to update user. Error: {e}")
            await self.db.rollback()
            raise
