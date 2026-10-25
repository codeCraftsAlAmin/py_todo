from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from loguru import logger

from .config.db import Base, engine
from .config.exceptions import register_exception_handlers
from .models import (
    todos_model,  # noqa: F401
    users_model,  # noqa: F401
)
from .routers import user_router


# manage application lifecycles gracefully (Startup and Shutdown events)
@asynccontextmanager
async def lifespan(app: FastAPI):

    async with engine.begin() as conn:
        logger.info("🚀 Starting up FastAPI application and connecting to database...")
        await conn.run_sync(Base.metadata.create_all)
    # startup task
    yield
    # shut down task
    await engine.dispose()
    logger.warning(
        "🛑 Database connection closed gracefully. Application shutting down."
    )


app = FastAPI(title="Todo Application", version="1.0.0", lifespan=lifespan)
add_pagination(app)


app.include_router(user_router.router)


@app.get("/")
def read_root():
    return {"message": "PyTodo's API is runnig"}


# handle error
register_exception_handlers(app)
