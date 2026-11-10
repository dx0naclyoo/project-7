from datetime import UTC, datetime

import asyncpg
from fastapi import HTTPException

from settings import SESSION_TTL
from src.users.repository import SessionRepository, UserRepository
from src.users.schemas import SessionResponse, UserCreate, UserLogin, UserResponse
from src.users.security import hash_password, new_token, verify_password


class UserService:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.repo = UserRepository(conn)
        self.sessions = SessionRepository(conn)

    async def create(self, data: UserCreate) -> UserResponse:
        try:
            user = await self.repo.create(data.username, hash_password(data.password))
        except asyncpg.UniqueViolationError:
            raise HTTPException(status_code=409, detail="Username already taken")
        if user is None:
            raise HTTPException(status_code=500, detail="Failed to create user")
        return user

    async def delete(self, user_id: int) -> None:
        if not await self.repo.delete(user_id):
            raise HTTPException(status_code=404, detail="User not found")

    async def login(self, data: UserLogin) -> SessionResponse:
        found = await self.repo.get_credentials(data.username)
        # одна ошибка на "нет пользователя" и "неверный пароль": не подсказываем, что есть
        if found is None or not verify_password(data.password, found[1]):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        user = found[0]
        token = new_token()
        expires_at = datetime.now(UTC) + SESSION_TTL
        await self.sessions.create(token, user.id, expires_at)
        return SessionResponse(token=token, expires_at=expires_at, user=user)

    async def logout(self, token: str) -> None:
        # повторный выход не ошибка: сессии уже нет
        await self.sessions.delete(token)

    async def current(self, token: str) -> UserResponse:
        user = await self.sessions.get_user(token)
        if user is None:
            raise HTTPException(status_code=401, detail="Session expired")
        return user
