from settings import (
    CARDIO_NAME,
    DAY_NAMES,
    DEFAULT_LEVEL,
    DEFAULT_REPS,
    EXERCISES,
    LEVEL_VOLUME,
    REPS_BY_GOAL,
    SPLITS,
)
from src.training_plan.schemas import Exercise, PlanDay


def generate_plan(level: str, days: list[int], goal_type: str | None) -> list[PlanDay]:
    exercises_count, sets, cardio_minutes = LEVEL_VOLUME.get(
        level, LEVEL_VOLUME[DEFAULT_LEVEL]
    )
    reps = REPS_BY_GOAL.get(goal_type, DEFAULT_REPS) if goal_type else DEFAULT_REPS
    week_days = sorted(set(days))
    split = SPLITS[len(week_days)]

    plan = []
    for day, focus in zip(week_days, split, strict=True):
        exercises = [
            Exercise(name=name, sets=sets, reps=reps)
            for name in EXERCISES[focus][:exercises_count]
        ]
        if goal_type == "lose_weight":
            exercises.append(Exercise(name=CARDIO_NAME, sets=1, minutes=cardio_minutes))
        plan.append(
            PlanDay(day=day, day_name=DAY_NAMES[day], focus=focus, exercises=exercises)
        )
    return plan
