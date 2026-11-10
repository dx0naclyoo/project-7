from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.db import Connection
from src.users.schemas import SessionResponse, UserCreate, UserLogin, UserResponse
from src.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])

bearer = HTTPBearer(auto_error=False)


def get_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> str:
    """Токен из заголовка Authorization: Bearer <token>."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return credentials.credentials


Token = Annotated[str, Depends(get_token)]


@router.post("/", status_code=201, response_model=UserResponse)
async def create_user(data: UserCreate, conn: Connection) -> UserResponse:
    return await UserService(conn).create(data)


@router.post("/login", response_model=SessionResponse)
async def login(data: UserLogin, conn: Connection) -> SessionResponse:
    """Вход по имени и паролю. Токен живёт 30 дней (SESSION_TTL)."""
    return await UserService(conn).login(data)


@router.post("/logout", status_code=204)
async def logout(token: Token, conn: Connection) -> None:
    await UserService(conn).logout(token)


@router.get("/me", response_model=UserResponse)
async def me(token: Token, conn: Connection) -> UserResponse:
    """Кто вошёл. 401, если сессия истекла или токена нет."""
    return await UserService(conn).current(token)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, conn: Connection) -> None:
    await UserService(conn).delete(user_id)
