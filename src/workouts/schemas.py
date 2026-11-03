from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class WorkoutStart(BaseModel):
    user_id: int = Field(description="ID пользователя из таблицы users")


class WorkoutEnd(BaseModel):
    user_id: int = Field(description="ID пользователя из таблицы users")


class WorkoutResponse(BaseModel):
    id: int
    user_id: int
    started_at: datetime
    ended_at: datetime | None
    calories: Decimal | None


class CaloriesResponse(BaseModel):
    workout_id: int
    user_id: int
    level: str
    met: float = Field(description="Метаболический эквивалент для уровня тренировки")
    weight: Decimal = Field(description="Вес пользователя в кг")
    duration_minutes: float
    calories: Decimal = Field(description="Сожжённые калории (ккал)")
