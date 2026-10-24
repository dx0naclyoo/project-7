import asyncpg
from fastapi import HTTPException

from src.parameters.repository import ParametersRepository
from src.parameters.schemas import UserParametersCreate, UserParametersResponse
from src.users.repository import UserRepository


class ParametersService:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.users = UserRepository(conn)
        self.repo = ParametersRepository(conn)

    async def save(self, data: UserParametersCreate) -> UserParametersResponse:
        if not await self.users.exists(data.user_id):
            raise HTTPException(status_code=404, detail="User not found")
        result = await self.repo.upsert(data)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to save parameters")
        return result

    async def get(self, user_id: int) -> UserParametersResponse:
        result = await self.repo.get(user_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Parameters not found")
        return result
