from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, status

from ..config.dependencies import SessionDep
from ..config.security import get_current_user
from ..models.users_model import User
from ..repositories.todo_repository import TodoRepository
from ..schemas.todos_schema import TodoCreate, TodoResponse
from ..services import todo_service

router = APIRouter(prefix="/api/todos", tags=["Todos"])

CurrentUser: TypeAlias = Annotated[User, Depends(get_current_user)]
# ParamsDep: TypeAlias = Annotated[Params, Depends()]


# get todos
@router.get("/", status_code=status.HTTP_200_OK)
async def read_todos(db: SessionDep):
    return {"message": "this is read todo router"}


# get own todos
@router.get("/my-todos", status_code=status.HTTP_200_OK)
async def get_my_todos(db: SessionDep, current_user: CurrentUser):
    todo_repo = TodoRepository(db)
    get_own_todos_service = todo_service.TodoService(todo_repo)

    items = await get_own_todos_service.get_own_todos(id=current_user.id)
    return {"items": items}


# create todo
@router.post(
    "/create", response_model=TodoResponse, status_code=status.HTTP_201_CREATED
)
async def create_todo(
    todo_payload: TodoCreate, db: SessionDep, current_user: CurrentUser
):
    todo_repo = TodoRepository(db)

    create_todo_service = todo_service.TodoService(todo_repo)
    return await create_todo_service.create_todo(
        id=current_user.id, todo_payload=todo_payload
    )


# delete todo
@router.delete("{id}/delete", status_code=status.HTTP_200_OK)
async def delete_todo(id: int, db: SessionDep):
    return {"message": "this is delete todo router"}


# update todo
@router.patch("/{id}/update", status_code=status.HTTP_200_OK)
async def update_todo(id: int, db: SessionDep):
    return {"message": "this is update todo router"}
