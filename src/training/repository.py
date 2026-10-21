import asyncpg

from src.training.schemas import TrainingSettingsCreate, TrainingSettingsResponse


class TrainingSettingsRepository:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.conn = conn

    async def upsert(self, data: TrainingSettingsCreate) -> TrainingSettingsResponse | None:
        row = await self.conn.fetchrow(
            "INSERT INTO training_settings (user_id, level, days) "
            "VALUES ($1, $2, $3) "
            "ON CONFLICT (user_id) DO UPDATE "
            "SET level = EXCLUDED.level, days = EXCLUDED.days "
            "RETURNING id, user_id, level, days",
            data.user_id,
            data.level.value,
            data.days,
        )
        return TrainingSettingsResponse(**dict(row)) if row else None

    async def get(self, user_id: int) -> TrainingSettingsResponse | None:
        row = await self.conn.fetchrow(
            "SELECT id, user_id, level, days FROM training_settings WHERE user_id = $1",
            user_id,
        )
        return TrainingSettingsResponse(**dict(row)) if row else None