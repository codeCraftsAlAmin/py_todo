from ..models.todos_model import Todo
from ..repositories.todo_repository import TodoRepository
from ..schemas.todos_schema import TodoCreate


class TodoService:
    def __init__(self, todo_repo: TodoRepository):
        self.todo_repo = todo_repo

    async def get_own_todos(self, id: int) -> list[Todo | None]:
        todo = await self.todo_repo.own_todos(id=id)

        return todo

    async def create_todo(self, id: int, todo_payload: TodoCreate) -> Todo:

        todo = todo_payload.model_dump()
        todo["user_id"] = id

        todo_data = Todo(**todo)
        return await self.todo_repo.create(todo_data)

    async def read_todos(self) -> Todo:
        return await self.todo_repo.read()
