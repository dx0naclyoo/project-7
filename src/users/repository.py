from datetime import datetime

import asyncpg

from src.users.schemas import UserResponse


class UserRepository:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.conn = conn

    async def exists(self, user_id: int) -> bool:
        row = await self.conn.fetchrow("SELECT id FROM users WHERE id = $1", user_id)
        return row is not None

    async def create(self, username: str, password_hash: str) -> UserResponse | None:
        row = await self.conn.fetchrow(
            "INSERT INTO users (username, password_hash) VALUES ($1, $2) "
            "RETURNING id, username",
            username,
            password_hash,
        )
        return UserResponse(**dict(row)) if row else None

    async def get_credentials(self, username: str) -> tuple[UserResponse, str] | None:
        """Пользователь и хэш пароля. None, если нет пользователя или пароля."""
        row = await self.conn.fetchrow(
            "SELECT id, username, password_hash FROM users "
            "WHERE username = $1 AND password_hash IS NOT NULL",
            username,
        )
        if row is None:
            return None
        return UserResponse(id=row["id"], username=row["username"]), row["password_hash"]

    async def delete(self, user_id: int) -> bool:
        async with self.conn.transaction():
            await self.conn.execute("DELETE FROM goals WHERE user_id = $1", user_id)
            await self.conn.execute("DELETE FROM parameters WHERE user_id = $1", user_id)
            row = await self.conn.fetchrow(
                "DELETE FROM users WHERE id = $1 RETURNING id", user_id
            )
        return row is not None


class SessionRepository:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.conn = conn

    async def create(self, token: str, user_id: int, expires_at: datetime) -> None:
        # заодно чистим истёкшие сессии этого пользователя
        async with self.conn.transaction():
            await self.conn.execute(
                "DELETE FROM sessions WHERE user_id = $1 AND expires_at <= now()",
                user_id,
            )
            await self.conn.execute(
                "INSERT INTO sessions (token, user_id, expires_at) VALUES ($1, $2, $3)",
                token,
                user_id,
                expires_at,
            )

    async def get_user(self, token: str) -> UserResponse | None:
        """Владелец живой сессии или None."""
        row = await self.conn.fetchrow(
            "SELECT u.id, u.username FROM sessions s JOIN users u ON u.id = s.user_id "
            "WHERE s.token = $1 AND s.expires_at > now()",
            token,
        )
        return UserResponse(**dict(row)) if row else None

    async def delete(self, token: str) -> bool:
        row = await self.conn.fetchrow(
            "DELETE FROM sessions WHERE token = $1 RETURNING token", token
        )
        return row is not None
