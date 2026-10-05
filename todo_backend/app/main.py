import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .config.db import Base, engine
from .config.exceptions import UserAlreadyExistsError
from .models import users_model  # noqa: F401
from .routers import user_router

app = FastAPI()

# login setup for finding out the error
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# db connection
Base.metadata.create_all(bind=engine)

app.include_router(user_router.router)


@app.get("/")
def read_root():
    return {"message": "PyTodo's API is runnig"}


# custom error handler for business login
@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "details": f"Email '{exc.email}' is already registered",
        },
    )


# input validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    logger.error(f"❌ Validation Error at {request.url.path}")
    logger.error(f"Details: {exc.errors()}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=({"detail": exc.errors(), "body": exc.body}),
    )
