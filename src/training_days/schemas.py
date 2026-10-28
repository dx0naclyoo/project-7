from pydantic import BaseModel, Field, field_validator

from src.training.schemas import Day


class TrainingDaysSet(BaseModel):
    user_id: int = Field(description="ID пользователя из таблицы users")
    days: list[Day] = Field(
    min_length=1, max_length=7, description="Дни тренировок: от 1 (пн) до 7 (вс)"
        )

    @field_validator("days")
    @classmethod
    def unique_sorted(cls, value: list[int]) -> list[int]:
        return sorted(set(value))


class TrainingDaysResponse(BaseModel):
    user_id: int
    days: list[int]