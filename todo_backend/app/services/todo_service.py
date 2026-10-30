from ..config.exceptions import TodoNotFound
from ..models.todos_model import Todo
from ..repositories.todo_repository import TodoRepository
from ..schemas.todos_schema import TodoCreate, UpdateTodo


class TodoService:
    def __init__(self, todo_repo: TodoRepository):
        self.todo_repo = todo_repo

    async def get_own_todos(self, id: int) -> list[Todo | None]:
        todo = await self.todo_repo.own_todos(id=id)
        return todo

    async def find_by_id(self, id: int, user_id: int) -> Todo | None:
        todo = await self.todo_repo.find(id=id, user_id=user_id)

        if todo is None:
            raise TodoNotFound(id=id)
        return todo

    async def create_todo(self, id: int, todo_payload: TodoCreate) -> Todo:

        todo = todo_payload.model_dump()
        todo["user_id"] = id

        todo_data = Todo(**todo)
        return await self.todo_repo.create(todo_data)

    async def delete_todo(self, id: int, user_id: int):
        todo = await self.todo_repo.find(id=id, user_id=user_id)

        if todo is None:
            raise TodoNotFound(id=id)
        await self.todo_repo.delete(todo=todo)

    async def update_todo(self, id: int, payload: UpdateTodo, user_id: int) -> Todo:
        todo = await self.todo_repo.find(id=id, user_id=user_id)

        if todo is None:
            raise TodoNotFound(id=id)

        updated_data = payload.model_dump(exclude_unset=True)

        for key, value in updated_data.items():
            setattr(todo, key, value)

        updated_todo = await self.todo_repo.update(todo_data=todo)
        return updated_todo
