from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class Level(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    hard = "hard"


Day = Annotated[int, Field(ge=1, le=7)]


class TrainingSettingsCreate(BaseModel):
    user_id: int = Field(description="ID пользователя из таблицы users")
    level: Level = Field(description="Уровень: beginner, intermediate или hard")
    days: list[Day] = Field(
        min_length=1, max_length=7, description="Дни тренировок: от 1 (пн) до 7 (вс)"
    )

    @field_validator("days")
    @classmethod
    def unique_sorted(cls, value: list[int]) -> list[int]:
        return sorted(set(value))


class TrainingSettingsResponse(BaseModel):
    id: int
    user_id: int
    level: str
    days: list[int]