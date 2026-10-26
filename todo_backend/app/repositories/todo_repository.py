from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.todos_model import Todo


class TodoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id: int) -> Todo | None:
        result = await self.db.execute(select(Todo).where(Todo.id == id))
        return result.scalars().first()

    async def create(self, todo_payload: Todo) -> Todo:
        try:
            self.db.add(todo_payload)
            await self.db.commit()
            await self.db.refresh(todo_payload)
            return todo_payload
        except Exception as e:
            logger.error(f"Failed to create user. Error: {e}")
            raise

    async def read(self) -> Todo:
        try:
            result = await self.db.execute(select(Todo))
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to delete user. Error: {e}")
            raise
