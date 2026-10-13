from typing import Annotated, TypeAlias

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.db import get_db

SessionDep: TypeAlias = Annotated[AsyncSession, Depends(get_db)]
