from decimal import ROUND_HALF_UP, Decimal

import asyncpg
from fastapi import HTTPException

from settings import DEFAULT_LEVEL, MET_BY_LEVEL
from src.parameters.repository import ParametersRepository
from src.users.repository import UserRepository
from src.workouts.repository import WorkoutRepository
from src.workouts.schemas import CaloriesResponse, WorkoutResponse


class WorkoutService:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.conn = conn
        self.users = UserRepository(conn)
        self.parameters = ParametersRepository(conn)
        self.repo = WorkoutRepository(conn)

    async def start(self, user_id: int) -> WorkoutResponse:
        if not await self.users.exists(user_id):
            raise HTTPException(status_code=404, detail="User not found")
        if await self.repo.get_active(user_id) is not None:
            raise HTTPException(status_code=409, detail="Workout already started")
        try:
            result = await self.repo.start(user_id)
        except asyncpg.UniqueViolationError:
            # параллельный запрос успел создать тренировку раньше
            raise HTTPException(status_code=409, detail="Workout already started")
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to start workout")
        return result

    async def end(self, user_id: int) -> WorkoutResponse:
        if not await self.users.exists(user_id):
            raise HTTPException(status_code=404, detail="User not found")
        async with self.conn.transaction():
            workout = await self.repo.end(user_id)
            if workout is None:
                raise HTTPException(status_code=404, detail="No active workout")
            calories = await self._calculate(workout)
            await self.repo.set_calories(workout.id, calories.calories)
        workout.calories = calories.calories
        return workout

    async def calories(self, workout_id: int) -> CaloriesResponse:
        workout = await self.repo.get(workout_id)
        if workout is None:
            raise HTTPException(status_code=404, detail="Workout not found")
        return await self._calculate(workout)

    async def _calculate(self, workout: WorkoutResponse) -> CaloriesResponse:
        if workout.ended_at is None:
            raise HTTPException(status_code=400, detail="Workout is not finished yet")
        params = await self.parameters.get(workout.user_id)
        if params is None:
            raise HTTPException(
                status_code=400, detail="User parameters (weight) not set"
            )
        level = await self.repo.get_level(workout.user_id) or DEFAULT_LEVEL
        met = MET_BY_LEVEL.get(level, MET_BY_LEVEL[DEFAULT_LEVEL])

        seconds = (workout.ended_at - workout.started_at).total_seconds()
        hours = Decimal(str(seconds)) / Decimal(3600)

        # ккал = MET * вес (кг) * время (ч)
        calories = (Decimal(str(met)) * params.weight * hours).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return CaloriesResponse(
            workout_id=workout.id,
            user_id=workout.user_id,
            level=level,
            met=met,
            weight=params.weight,
            duration_minutes=round(seconds / 60, 2),
            calories=calories,
        )
