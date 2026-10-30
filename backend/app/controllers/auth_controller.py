from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dbconfig import get_db_session
from app.models.entities import User
from app.schemas.auth_schema import ErrorResponse, LoginRequest, LoginResponse, RegisterRequest, UserPublic
from app.services.auth_service import (
    AuthError,
    authenticate_current_user,
    create_access_token,
    DuplicateEmailError,
    InvalidCredentialsError,
    login_user,
    PasswordTooLongError,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    try:
        if credentials is None:
            raise AuthError("Missing authorization header")
        token = credentials.credentials
        return await authenticate_current_user(token, session)
    except AuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Password too long for bcrypt."},
        409: {"model": ErrorResponse, "description": "Email already registered."},
        422: {"description": "Validation error."},
    },
)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_db_session)) -> UserPublic:
    try:
        user = await register_user(session, payload.name, str(payload.email), payload.password)
    except PasswordTooLongError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return UserPublic(id=user.id, name=user.name, email=user.email, role=user.role, created_at=user.created_at)


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid email or password."},
        422: {"description": "Validation error."},
    },
)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_db_session)) -> LoginResponse:
    try:
        user = await login_user(session, str(payload.email), payload.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    return LoginResponse(
        access_token=create_access_token(user.id),
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get(
    "/me",
    response_model=UserPublic,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Missing, invalid, tampered, expired token, or user no longer exists.",
        }
    },
)
async def me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at,
    )
