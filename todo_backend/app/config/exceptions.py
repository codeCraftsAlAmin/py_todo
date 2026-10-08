from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class BaseAppException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UserAlreadyExistsError(BaseAppException):
    def __init__(self, email: str):
        super().__init__(
            message=f"Email '{email}' is already registered",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class UserNotFoundError(BaseAppException):
    def __init__(self, id: int):
        super().__init__(
            message=f"User with ID {id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


def register_exception_handlers(app: FastAPI) -> None:
    # handle server error
    @app.exception_handler(BaseAppException)
    async def user_already_exists_handler(request: Request, exc: BaseAppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"details": exc.message},
        )

    # handle input error
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"Input validation failed"},
        )
