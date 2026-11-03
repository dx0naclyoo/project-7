from datetime import datetime

from pydantic import BaseModel, Field


class Exercise(BaseModel):
    name: str
    sets: int = Field(description="Количество подходов")
    reps: int | None = Field(default=None, description="Повторений в подходе")
    minutes: int | None = Field(default=None, description="Длительность для кардио")


class PlanDay(BaseModel):
    day: int = Field(description="День недели: от 1 (пн) до 7 (вс)")
    day_name: str
    focus: str = Field(description="Группа мышц: push, pull, legs, upper, lower, full_body")
    exercises: list[Exercise]


class TrainingPlanResponse(BaseModel):
    id: int
    user_id: int
    level: str
    goal_type: str | None
    days: list[PlanDay]
    created_at: datetime
