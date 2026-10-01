from datetime import datetime

from pydantic import BaseModel, EmailStr


# Base fields shared across creation and responses
class UserBase(BaseModel):
    user_name: str
    email: EmailStr


# Used for registration/creation (Incoming Request)
class UserCreate(UserBase):
    password: str


# Used for API responses (Outgoing Data)
class User(UserBase):
    id: int
    is_deleted: bool
    is_admin: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
    }
