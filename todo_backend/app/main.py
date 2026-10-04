from fastapi import FastAPI

from .config.db import Base, engine
from .models import users_model  # noqa: F401
from .routers import user_router

app = FastAPI()

# db connection
Base.metadata.create_all(bind=engine)

app.include_router(user_router.router)


@app.get("/")
def read_root():
    return {"message": "PyTodo's API is runnig"}
