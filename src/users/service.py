import asyncpg
from fastapi import HTTPException

from src.users.repository import UserRepository
from src.users.schemas import UserCreate, UserResponse


class UserService:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.repo = UserRepository(conn)

    async def create(self, data: UserCreate) -> UserResponse:
        user = await self.repo.create(data)
        if user is None:
            raise HTTPException(status_code=500, detail="Failed to create user")
        return user

    async def delete(self, user_id: int) -> None:
        if not await self.repo.delete(user_id):
            raise HTTPException(status_code=404, detail="User not found")
