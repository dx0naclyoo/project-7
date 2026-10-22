import asyncpg
from fastapi import HTTPException

from src.parameters.repository import ParametersRepository
from src.parameters.schemas import UserParametersCreate, UserParametersResponse
from src.users.repository import UserRepository


class ParametersService:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.users = UserRepository(conn)
        self.repo = ParametersRepository(conn)

    async def create(self, data: UserParametersCreate) -> UserParametersResponse:
        if not await self.users.exists(data.user_id):
            raise HTTPException(status_code=404, detail="User not found")
        result = await self.repo.create(data)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to save parameters")
        return result
