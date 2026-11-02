from fastapi import APIRouter

from src.db import Connection
from src.training_days.schemas import TrainingDaysResponse, TrainingDaysSet
from src.training_days.service import TrainingDaysService

router = APIRouter(prefix="/users/training-days", tags=["training"])


@router.put("/", response_model=TrainingDaysResponse)
async def set_days_trainings(
    data: TrainingDaysSet, conn: Connection
) -> TrainingDaysResponse:
    return await TrainingDaysService(conn).set_days(data)


@router.get("/{user_id}", response_model=TrainingDaysResponse)
async def get_days(user_id: int, conn: Connection) -> TrainingDaysResponse:
    return await TrainingDaysService(conn).get_days(user_id)