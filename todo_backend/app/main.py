from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from .config.db import Base, engine
from .config.exceptions import UserAlreadyExistsError
from .models import users_model  # noqa: F401
from .routers import user_router

app = FastAPI()

# db connection
Base.metadata.create_all(bind=engine)

app.include_router(user_router.router)


@app.get("/")
def read_root():
    return {"message": "PyTodo's API is runnig"}


# handle global error
@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "details": f"Email '{exc.email}' is already registered",
        },
    )
