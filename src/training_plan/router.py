from fastapi import APIRouter

from src.db import Connection
from src.training_plan.schemas import TrainingPlanResponse
from src.training_plan.service import TrainingPlanService

router = APIRouter(prefix="/users/training-plan", tags=["training"])


@router.get("/{user_id}", response_model=TrainingPlanResponse)
async def get_training_plan(user_id: int, conn: Connection) -> TrainingPlanResponse:
    """План пользователя. При первом запросе собирается из настроек и цели."""
    return await TrainingPlanService(conn).get_or_create(user_id)


@router.post("/{user_id}/regenerate", response_model=TrainingPlanResponse)
async def regenerate_training_plan(
    user_id: int, conn: Connection
) -> TrainingPlanResponse:
    """Пересобрать план, например после смены уровня, дней или цели."""
    return await TrainingPlanService(conn).regenerate(user_id)
