from ..config.exceptions import TodoNotFound
from ..models.todos_model import Todo
from ..repositories.todo_repository import TodoRepository
from ..schemas.todos_schema import TodoCreate


class TodoService:
    def __init__(self, todo_repo: TodoRepository):
        self.todo_repo = todo_repo

    async def get_own_todos(self, id: int) -> list[Todo | None]:
        todo = await self.todo_repo.own_todos(id=id)

        if todo is None: 
            raise TodoNotFound()
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
