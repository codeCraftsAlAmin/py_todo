import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated, TypeAlias

import jwt
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import APIKeyCookie, OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.exceptions import UserNotFoundError
from ..config.logger import logger
from ..config.settings import setting
from ..models.users_model import User
from ..repositories import user_repository
from ..utils.token_service import create_token_family, rotate_family_token
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


# to use refresh in redis
def _build_refresh_jwt(user_id: str, family_id: str, ttl_seconds: int) -> str:
    expire = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
    payload = {
        "sub": user_id,
        "fid": family_id,
        "jti": str(uuid.uuid4()),  # to confirm unique hash in each rotaion
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, setting.SECRET_KEY, setting.ALGORITHM)


# create refresh token
async def create_refresh_token(data: dict) -> str:
    user_id = str(data["sub"])
    family_id = str(uuid.uuid4())
    idle_ttl = setting.REFRESH_TOKEN_IDLE_DAYS * 24 * 60 * 60

    raw_refresh_token = _build_refresh_jwt(user_id, family_id, idle_ttl)
    await create_token_family(
        user_id=user_id, family_id=family_id, raw_refresh_token=raw_refresh_token
    )
    return raw_refresh_token


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

    try:
        user_uuid = uuid.UUID(str(user_id))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier in token",
        )

    user_repo = user_repository.UserRepository(db)
    user = await user_repo.get_by_id(user_uuid)

    if user is None:
        raise UserNotFoundError(id=user_id)
    logger.info(f"user info : {user}")
    return user


# regenrate access token
async def regenerate_access_token(request: Request) -> dict[str, str]:
    submitted_refresh_token = request.cookies.get("refresh_token")
    if not submitted_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )
    try:
        payload = jwt.decode(
            submitted_refresh_token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM]
        )
        user_id: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")
        family_id: str | None = payload.get("fid")

        if not family_id or not user_id or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token structure",
            )

        try:
            uuid.UUID(str(user_id))
            uuid.UUID(str(family_id))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Malformed token identifiers",
            )

        idle_ttl = setting.REFRESH_TOKEN_IDLE_DAYS * 24 * 60 * 60
        new_refresh_token = _build_refresh_jwt(
            user_id=user_id, family_id=family_id, ttl_seconds=idle_ttl
        )

        # atomic rotaition & reuse detection
        is_valid, message, effective_ttl = await rotate_family_token(
            user_id,
            family_id,
            submitted_refresh_token,
            new_raw_token=new_refresh_token,
        )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=message
            )

        new_access_token = create_access_token(data={"sub": str(user_id)})
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "refresh_max_age": effective_ttl,
            "token_type": "bearer",
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired. Please log in again.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


# set cookies
def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str | None = None,
    refresh_max_age: int | None = None,
):
    secure = setting.ENVIRONMENT == "production"

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # stay hide from js
        secure=secure,  # will be True in production(HTTPS)
        samesite="lax",
        max_age=setting.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    if refresh_token:
        max_age = refresh_max_age or (setting.REFRESH_TOKEN_IDLE_DAYS * 24 * 60 * 60)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,  # stay hide from js
            secure=secure,  # will be True in production
            samesite="lax",
            max_age=max_age,
        )


# remove cookies
def remove_auth_cookies(response: Response):
    secure = setting.ENVIRONMENT == "production"

    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=secure,
        samesite="lax",
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=secure,
        samesite="lax",
    )
