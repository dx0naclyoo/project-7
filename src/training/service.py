import asyncpg
from fastapi import HTTPException

from src.training.repository import TrainingSettingsRepository
from src.training.schemas import TrainingSettingsCreate, TrainingSettingsResponse
from src.users.repository import UserRepository


class TrainingSettingsService:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.users = UserRepository(conn)
        self.repo = TrainingSettingsRepository(conn)

    async def save(self, data: TrainingSettingsCreate) -> TrainingSettingsResponse:
        if not await self.users.exists(data.user_id):
            raise HTTPException(status_code=404, detail="User not found")
        result = await self.repo.upsert(data)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to save training settings")
        return result

    async def get(self, user_id: int) -> TrainingSettingsResponse:
        result = await self.repo.get(user_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Training settings not found")
        return result