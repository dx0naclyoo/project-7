import json

import asyncpg

from src.training_plan.schemas import PlanDay, TrainingPlanResponse


def row_to_plan(row: asyncpg.Record) -> TrainingPlanResponse:
    data = dict(row)
    # asyncpg отдаёт JSONB строкой
    data["days"] = json.loads(data["days"])
    return TrainingPlanResponse(**data)


def days_to_json(days: list[PlanDay]) -> str:
    return json.dumps([day.model_dump() for day in days], ensure_ascii=False)
