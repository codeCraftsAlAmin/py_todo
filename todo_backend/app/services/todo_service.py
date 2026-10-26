from ..config.exceptions import TodoNotFound
from ..models.todos_model import Todo
from ..repositories.todo_repository import TodoRepository
from ..schemas.todos_schema import TodoCreate


class TodoService:
    def __init__(self, todo_repo: TodoRepository):
        self.todo_repo = todo_repo

    async def get_todo_by_id(self, id: int) -> Todo:
        todo = await self.todo_repo.get_by_id(id=id)
        if todo is None:
            raise TodoNotFound(id=id)

        return todo

    async def create_todo(self, id: int, todo_payload: TodoCreate) -> Todo:
        todo_data = await self.todo_repo.create(todo_payload)
        
        return todo_data

    async def read_todos(self) -> Todo:
        return await self.todo_repo.read()
