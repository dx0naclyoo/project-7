import asyncpg
from fastapi import HTTPException

from src.goals.repository import GoalRepository
from src.training.repository import TrainingSettingsRepository
from src.training_plan.generator import generate_plan
from src.training_plan.repository import TrainingPlanRepository
from src.training_plan.schemas import PlanDay, TrainingPlanResponse
from src.users.repository import UserRepository


class TrainingPlanService:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.users = UserRepository(conn)
        self.settings = TrainingSettingsRepository(conn)
        self.goals = GoalRepository(conn)
        self.repo = TrainingPlanRepository(conn)

    async def get_or_create(self, user_id: int) -> TrainingPlanResponse:
        """Отдаёт сохранённый план; если его нет, собирает и сохраняет."""
        if not await self.users.exists(user_id):
            raise HTTPException(status_code=404, detail="User not found")
        plan = await self.repo.get(user_id)
        if plan is not None:
            return plan

        level, goal_type, days = await self._build(user_id)
        created = await self.repo.create_if_absent(user_id, level, goal_type, days)
        # параллельный запрос мог успеть сохранить план раньше: отдаём его
        result = created or await self.repo.get(user_id)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to save training plan")
        return result

    async def regenerate(self, user_id: int) -> TrainingPlanResponse:
        """Пересобирает план по текущим настройкам и цели."""
        if not await self.users.exists(user_id):
            raise HTTPException(status_code=404, detail="User not found")
        level, goal_type, days = await self._build(user_id)
        result = await self.repo.replace(user_id, level, goal_type, days)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to save training plan")
        return result

    async def _build(self, user_id: int) -> tuple[str, str | None, list[PlanDay]]:
        settings = await self.settings.get(user_id)
        if settings is None:
            raise HTTPException(
                status_code=404,
                detail="Training settings not found, create them first "
                "via POST /users/training-settings/",
            )
        goal = await self.goals.get(user_id)
        goal_type = goal.goal_type if goal else None
        days = generate_plan(settings.level, settings.days, goal_type)
        return settings.level, goal_type, days
