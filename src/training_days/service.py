import asyncpg
from fastapi import HTTPException

from src.training_days.repository import TrainingDaysRepository
from src.training_days.schemas import TrainingDaysResponse, TrainingDaysSet
from src.users.repository import UserRepository


class TrainingDaysService:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.users = UserRepository(conn)
        self.repo = TrainingDaysRepository(conn)

    async def set_days(self, data: TrainingDaysSet) -> TrainingDaysResponse:
        if not await self.users.exists(data.user_id):
            raise HTTPException(status_code=404, detail="User not found")
        result = await self.repo.set_days(data)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to save training days")
        return result

    async def get_days(self, user_id: int) -> TrainingDaysResponse:
        result = await self.repo.get_days(user_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Training days not found")
        return result