from fastapi import APIRouter

from src.db import Connection
from src.workouts.schemas import (
    CaloriesResponse,
    WorkoutEnd,
    WorkoutResponse,
    WorkoutStart,
)
from src.workouts.service import WorkoutService

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("/start-train", status_code=201, response_model=WorkoutResponse)
async def start_train(data: WorkoutStart, conn: Connection) -> WorkoutResponse:
    return await WorkoutService(conn).start(data.user_id)


@router.post("/end-train", response_model=WorkoutResponse)
async def end_train(data: WorkoutEnd, conn: Connection) -> WorkoutResponse:
    return await WorkoutService(conn).end(data.user_id)


@router.get("/{workout_id}/calories", response_model=CaloriesResponse)
async def get_calories(workout_id: int, conn: Connection) -> CaloriesResponse:
    return await WorkoutService(conn).calories(workout_id)
