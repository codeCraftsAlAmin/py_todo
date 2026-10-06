from fastapi import status


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
