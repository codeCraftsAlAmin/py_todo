from typing import Annotated, TypeAlias

from fastapi import Depends
from sqlalchemy.orm import Session

from ..config.db import get_db

SessionDep: TypeAlias = Annotated[Session, Depends(get_db)]
