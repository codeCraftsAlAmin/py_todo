from fastapi import FastAPI
from fastapi_pagination import add_pagination

from .config.db import Base, engine
from .config.exceptions import register_exception_handlers
from .models import users_model  # noqa: F401
from .routers import user_router

app = FastAPI()
add_pagination(app)


# db connection
Base.metadata.create_all(bind=engine)

app.include_router(user_router.router)


@app.get("/")
def read_root():
    return {"message": "PyTodo's API is runnig"}


# handle error
register_exception_handlers(app)
