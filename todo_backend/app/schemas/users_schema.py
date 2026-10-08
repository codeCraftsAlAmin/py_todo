from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# Base fields shared across creation and responses
class UserBase(BaseModel):
    user_name: str = Field(..., description="username")
    email: EmailStr


# Used for registration/creation (Incoming Request)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="password")


class UserUpdate(BaseModel):
    user_name: str | None = Field(None, description="username")


# Used for API responses (Outgoing Data)
class UserResponse(UserBase):
    id: int
    is_deleted: bool
    is_admin: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
    }
