import asyncpg

from settings import PLAN_COLUMNS
from src.training_plan.helpers import days_to_json, row_to_plan
from src.training_plan.schemas import PlanDay, TrainingPlanResponse


class TrainingPlanRepository:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.conn = conn

    async def get(self, user_id: int) -> TrainingPlanResponse | None:
        row = await self.conn.fetchrow(
            f"SELECT {PLAN_COLUMNS} FROM training_plans WHERE user_id = $1",
            user_id,
        )
        return row_to_plan(row) if row else None

    async def create_if_absent(
        self, user_id: int, level: str, goal_type: str | None, days: list[PlanDay]
    ) -> TrainingPlanResponse | None:
        """Создаёт план. None, если план у пользователя уже есть."""
        row = await self.conn.fetchrow(
            "INSERT INTO training_plans (user_id, level, goal_type, days) "
            "VALUES ($1, $2, $3, $4::jsonb) "
            "ON CONFLICT (user_id) DO NOTHING "
            f"RETURNING {PLAN_COLUMNS}",
            user_id,
            level,
            goal_type,
            days_to_json(days),
        )
        return row_to_plan(row) if row else None

    async def replace(
        self, user_id: int, level: str, goal_type: str | None, days: list[PlanDay]
    ) -> TrainingPlanResponse | None:
        row = await self.conn.fetchrow(
            "INSERT INTO training_plans (user_id, level, goal_type, days) "
            "VALUES ($1, $2, $3, $4::jsonb) "
            "ON CONFLICT (user_id) DO UPDATE SET "
            "level = EXCLUDED.level, goal_type = EXCLUDED.goal_type, "
            "days = EXCLUDED.days, created_at = now() "
            f"RETURNING {PLAN_COLUMNS}",
            user_id,
            level,
            goal_type,
            days_to_json(days),
        )
        return row_to_plan(row) if row else None
