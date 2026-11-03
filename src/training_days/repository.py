import asyncpg

from src.training_days.schemas import TrainingDaysResponse, TrainingDaysSet


class TrainingDaysRepository:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.conn = conn

    async def set_days(self, data: TrainingDaysSet) -> TrainingDaysResponse | None:
        row = await self.conn.fetchrow(
            """
            UPDATE training_settings
            SET days = $2
            WHERE user_id = $1
            RETURNING user_id, days
            """,
            data.user_id,
            data.days,
        )
        return TrainingDaysResponse(**dict(row)) if row else None

    async def get_days(self, user_id: int) -> TrainingDaysResponse | None:
        row = await self.conn.fetchrow(
            """
            SELECT user_id, days
            FROM training_settings
            WHERE user_id = $1
            """,
            user_id,
        )
        return TrainingDaysResponse(**dict(row)) if row else None