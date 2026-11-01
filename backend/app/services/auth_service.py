from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.entities import User, UserRole

JWT_ALGORITHM = "HS256"
BCRYPT_MAX_PASSWORD_BYTES = 72


class AuthError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class DuplicateEmailError(Exception):
    pass


class PasswordTooLongError(Exception):
    pass


def normalize_email(email: str) -> str:
    return email.strip().lower()


def is_password_too_long(password: str) -> bool:
    return len(password.encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    if is_password_too_long(password):
        return False
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user_id: uuid.UUID) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )
    except jwt.PyJWTError:
        return None


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == normalize_email(email)))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


def is_duplicate_email_error(exc: IntegrityError) -> bool:
    original = getattr(exc, "orig", None)
    if original is None:
        return False

    message = str(original).lower()
    if "unique constraint failed" in message and "users.email" in message:
        return True

    sqlstate = getattr(original, "sqlstate", None)
    return sqlstate == "23505"


def extract_bearer_token(authorization_header: str | None) -> str:
    if not authorization_header:
        raise AuthError("Missing authorization header")

    parts = authorization_header.strip().split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
        raise AuthError("Invalid authorization header")
    return parts[1]


async def authenticate_current_user(token: str, session: AsyncSession) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise AuthError("Invalid token")

    try:
        user_id = uuid.UUID(str(payload["sub"]))
    except (ValueError, KeyError):
        raise AuthError("Invalid token payload")

    user = await get_user_by_id(session, user_id)
    if user is None:
        raise AuthError("User not found")
    return user


async def register_user(session: AsyncSession, name: str, email: str, password: str) -> User:
    if is_password_too_long(password):
        raise PasswordTooLongError("Password must not exceed 72 UTF-8 bytes.")

    existing_user = await get_user_by_email(session, email)
    if existing_user is not None:
        raise DuplicateEmailError("Email already registered")

    user = User(
        name=name.strip(),
        email=normalize_email(email),
        password_hash=hash_password(password),
        role=UserRole.MEMBER,
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        if is_duplicate_email_error(exc):
            raise DuplicateEmailError("Email already registered")
        raise

    await session.refresh(user)
    return user


async def login_user(session: AsyncSession, email: str, password: str) -> User:
    user = await get_user_by_email(session, email)
    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError("Invalid email or password")
    return user
