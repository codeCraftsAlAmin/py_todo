from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TodoStatus(str, Enum):
    RUNNING = "RUNNING"
    PENDING = "PENDING"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"


# Base fields shared across creation and responses
class TodoBase(BaseModel):
    title: str = Field(..., description="title")
    description: str | None = Field(None, description="describe your task")
    status: TodoStatus = TodoStatus.PENDING


class TodoCreate(TodoBase):
    pass


class TodoResponse(TodoBase):
    id: int
    user_id: int
    is_deleted: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
    }
