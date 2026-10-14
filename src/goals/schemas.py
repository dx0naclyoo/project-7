from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class GoalType(str, Enum):
    up_weight = "up_weight"
    lose_weight = "lose_weight"


class GoalCreate(BaseModel):
    user_id: int = Field(description="ID пользователя")
    goal_type: GoalType = Field(description="Цель: lose_weight или up_weight")
    target_weight: Decimal = Field(
        gt=0, le=120, max_digits=5, decimal_places=2, description="Вес в кг"
    )


class GoalResponse(BaseModel):
    id: int
    user_id: int
    goal_type: str
    target_weight: Decimal