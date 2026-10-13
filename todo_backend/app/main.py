from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_pagination import add_pagination

from .config.db import Base, engine
from .config.exceptions import register_exception_handlers
from .models import users_model  # noqa: F401
from .routers import user_router


# manage application lifecycles gracefully (Startup and Shutdown events)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup task
    yield
    # shut down task
    await engine.dispose()
    print("Database connection closed gracefully.")


app = FastAPI(title="Todo Application", version="1.0.0", lifespan=lifespan)
add_pagination(app)


# db connection
Base.metadata.create_all(bind=engine)

app.include_router(user_router.router)


@app.get("/")
def read_root():
    return {"message": "PyTodo's API is runnig"}


# handle error
register_exception_handlers(app)
