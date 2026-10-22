from fastapi import APIRouter

from src.db import Connection
from src.training.schemas import TrainingSettingsCreate, TrainingSettingsResponse
from src.training.service import TrainingSettingsService

router = APIRouter(prefix="/users/training-settings", tags=["training"])


@router.post("/", status_code=201, response_model=TrainingSettingsResponse)
async def save_training_settings(
    data: TrainingSettingsCreate, conn: Connection
) -> TrainingSettingsResponse:
    return await TrainingSettingsService(conn).save(data)


@router.get("/{user_id}", response_model=TrainingSettingsResponse)
async def get_training_settings(user_id: int, conn: Connection) -> TrainingSettingsResponse:
    return await TrainingSettingsService(conn).get(user_id)