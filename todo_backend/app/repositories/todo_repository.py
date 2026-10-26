from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.todos_model import Todo


class TodoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def own_todos(self, id: int) -> list[Todo | None]:
        result = await self.db.execute(select(Todo).where(Todo.user_id == id))
        return result.scalars().all()

    async def create(self, todo_data: Todo) -> Todo:
        try:
            self.db.add(todo_data)
            await self.db.commit()
            await self.db.refresh(todo_data)
            return todo_data
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
