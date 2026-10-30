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

    async def find(self, id: int, user_id: int) -> Todo | None:
        result = await self.db.execute(
            select(Todo).where(Todo.id == id, Todo.user_id == user_id)
        )

        return result.scalars().first()

    async def create(self, todo_data: Todo) -> Todo:
        try:
            self.db.add(todo_data)
            await self.db.commit()
            await self.db.refresh(todo_data)
            return todo_data
        except Exception as e:
            logger.error(f"Failed to create user. Error: {e}")
            raise

    async def delete(self, todo: Todo):
        try:
            await self.db.delete(todo)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete todo. Error: {e}")
            raise

    async def update(self, todo_data: Todo) -> Todo:
        try:
            update_todo = await self.db.merge(todo_data)
            await self.db.commit()
            await self.db.refresh(update_todo)
            return update_todo
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update todo. Error: {e}")
            raise
