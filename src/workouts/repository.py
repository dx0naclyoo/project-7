from decimal import Decimal

import asyncpg

from src.workouts.schemas import WorkoutResponse

WORKOUT_COLUMNS = "id, user_id, started_at, ended_at, calories"


class WorkoutRepository:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.conn = conn

    async def get_active(self, user_id: int) -> WorkoutResponse | None:
        row = await self.conn.fetchrow(
            f"SELECT {WORKOUT_COLUMNS} FROM workouts "
            "WHERE user_id = $1 AND ended_at IS NULL",
            user_id,
        )
        return WorkoutResponse(**dict(row)) if row else None

    async def get(self, workout_id: int) -> WorkoutResponse | None:
        row = await self.conn.fetchrow(
            f"SELECT {WORKOUT_COLUMNS} FROM workouts WHERE id = $1",
            workout_id,
        )
        return WorkoutResponse(**dict(row)) if row else None

    async def start(self, user_id: int) -> WorkoutResponse | None:
        row = await self.conn.fetchrow(
            f"INSERT INTO workouts (user_id) VALUES ($1) RETURNING {WORKOUT_COLUMNS}",
            user_id,
        )
        return WorkoutResponse(**dict(row)) if row else None

    async def end(self, user_id: int) -> WorkoutResponse | None:
        row = await self.conn.fetchrow(
            "UPDATE workouts SET ended_at = now() "
            "WHERE user_id = $1 AND ended_at IS NULL "
            f"RETURNING {WORKOUT_COLUMNS}",
            user_id,
        )
        return WorkoutResponse(**dict(row)) if row else None

    async def set_calories(self, workout_id: int, calories: Decimal) -> None:
        await self.conn.execute(
            "UPDATE workouts SET calories = $2 WHERE id = $1",
            workout_id,
            calories,
        )

    async def get_level(self, user_id: int) -> str | None:
        level: str | None = await self.conn.fetchval(
            "SELECT level FROM training_settings WHERE user_id = $1", user_id
        )
        return level
