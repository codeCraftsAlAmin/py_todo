from fastapi import APIRouter, status

from ..config.dependencies import SessionDep

router = APIRouter(prefix="/api/todos", tags=["Todos"])


# get todos
@router.get("/", status_code=status.HTTP_200_OK)
async def read_todos(db: SessionDep):
    return {"message": "this is read todo router"}


# get todo by id
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(id: int, db: SessionDep):
    return {"message": "this is read todo router"}


# create todo
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_todo(db: SessionDep):
    return {"message": "this is create todo router"}


# delete todo
@router.delete("{id}/delete", status_code=status.HTTP_200_OK)
async def delete_todo(id: int, db: SessionDep):
    return {"message": "this is delete todo router"}


# update todo
@router.patch("/{id}/update", status_code=status.HTTP_200_OK)
async def update_todo(id: int, db: SessionDep):
    return {"message": "this is update todo router"}
