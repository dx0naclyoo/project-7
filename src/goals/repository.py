import asyncpg

from src.goals.schemas import GoalCreate, GoalResponse


class GoalRepository:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.conn = conn

    async def upsert(self, data: GoalCreate) -> GoalResponse | None:
        row = await self.conn.fetchrow(
            "INSERT INTO goals (user_id, goal_type, target_weight) "
            "VALUES ($1, $2, $3) "
            "ON CONFLICT (user_id) DO UPDATE "
            "SET goal_type = EXCLUDED.goal_type, target_weight = EXCLUDED.target_weight "
            "RETURNING id, user_id, goal_type, target_weight",
            data.user_id,
            data.goal_type.value,
            data.target_weight,
        )
        return GoalResponse(**dict(row)) if row else None

    async def get(self, user_id: int) -> GoalResponse | None:
        row = await self.conn.fetchrow(
            "SELECT id, user_id, goal_type, target_weight FROM goals WHERE user_id = $1",
            user_id,
        )
        return GoalResponse(**dict(row)) if row else None
