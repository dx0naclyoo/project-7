import asyncpg
from fastapi import HTTPException

from src.goals.repository import GoalRepository
from src.goals.schemas import GoalCreate, GoalResponse
from src.users.repository import UserRepository


class GoalService:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.users = UserRepository(conn)
        self.repo = GoalRepository(conn)

    async def set_goal(self, data: GoalCreate) -> GoalResponse:
        if not await self.users.exists(data.user_id):
            raise HTTPException(status_code=404, detail="User not found")
        goal = await self.repo.upsert(data)
        if goal is None:
            raise HTTPException(status_code=500, detail="Failed to save goal")
        return goal

    async def get_goal(self, user_id: int) -> GoalResponse:
        goal = await self.repo.get(user_id)
        if goal is None:
            raise HTTPException(status_code=404, detail="Goal not found")
        return goal
