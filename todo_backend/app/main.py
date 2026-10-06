from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination

from .config.db import Base, engine
from .config.exceptions import BaseAppException
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


@app.exception_handler(BaseAppException)
async def user_already_exists_handler(request: Request, exc: BaseAppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"details": exc.message},
    )
