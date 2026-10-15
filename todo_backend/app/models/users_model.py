from datetime import datetime

from sqlalchemy import TIMESTAMP, Boolean, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..config.db import Base


class User(Base):
    __tablename__ = "users"
    id = Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, index=True
    )
    user_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )
