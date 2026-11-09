from datetime import UTC, datetime, timedelta
from typing import Annotated, TypeAlias

import jwt
from fastapi import Depends, HTTPException, Response, status
from fastapi.security import APIKeyCookie, OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.exceptions import UserNotFoundError
from ..config.logger import logger
from ..config.settings import setting
from ..models.users_model import User
from ..repositories import user_repository
from ..schemas.users_schema import RefreshTokenRequest
from .db import get_db

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/users/login")

# TokeDep: TypeAlias = Annotated[str, Depends(oauth2_scheme)]
SessionDep: TypeAlias = Annotated[AsyncSession, Depends(get_db)]
cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)


# hash password
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# create access token
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, setting.SECRET_KEY, setting.ALGORITHM)

    return encoded_jwt


# create refresh token
def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=setting.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, setting.SECRET_KEY, setting.ALGORITHM)

    return encoded_jwt


# get current user
async def get_current_user(
    access_token: Annotated[str | None, Depends(cookie_scheme)], db: SessionDep
) -> User:
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated, missing access token cookie",
        )
    try:
        payload = jwt.decode(
            access_token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM]
        )
        user_id = payload.get("sub")
        token_type = payload.get("type")

        if user_id is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated, missing access token cookie",
            )

    except InvalidTokenError as e:
        logger.error(f"Token validation failed. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user_repo = user_repository.UserRepository(db)
    user = await user_repo.get_by_id(int(user_id))

    if user is None:
        raise UserNotFoundError(id=user_id)
    logger.info(f"user info : {user}")
    return user


# regenrate access token
async def regenerate_access_token(body: RefreshTokenRequest) -> dict:
    try:
        token = body.refresh_token

        payload = jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
        user_id: int = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    except InvalidTokenError as e:
        logger.error(f"Token validation failed. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    new_access_token = create_access_token(data={"sub": str(user_id)})
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


# set cookies
def set_auth_cookies(
    response: Response, access_token: str, refresh_token: str | None = None
):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # stay hide from js
        secure=False,  # will be True in production(HTTPS)
        samesite="lax",
        max_age=15 * 60,  # 15m in sec
    )

    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,  # stay hide from js
            secure=False,  # will be True in production
            samesite="lax",
            max_age=7 * 24 * 60 * 60,  # 7ds in sec
        )


# remove cookies
def remove_auth_cookies(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,
        samesite="lax",
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,
        samesite="lax",
    )
