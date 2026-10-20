import asyncpg

from src.users.schemas import UserCreate, UserResponse


class UserRepository:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.conn = conn

    async def exists(self, user_id: int) -> bool:
        row = await self.conn.fetchrow("SELECT id FROM users WHERE id = $1", user_id)
        return row is not None

    async def create(self, data: UserCreate) -> UserResponse | None:
        row = await self.conn.fetchrow(
            "INSERT INTO users (username) VALUES ($1) RETURNING id, username",
            data.username,
        )
        return UserResponse(**dict(row)) if row else None

    async def delete(self, user_id: int) -> bool:
        async with self.conn.transaction():
            await self.conn.execute("DELETE FROM goals WHERE user_id = $1", user_id)
            await self.conn.execute("DELETE FROM parameters WHERE user_id = $1", user_id)
            row = await self.conn.fetchrow(
                "DELETE FROM users WHERE id = $1 RETURNING id", user_id
            )
        return row is not None
