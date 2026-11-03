"""Общие константы проекта."""

# Колонки таблицы workouts, которые возвращают запросы репозитория
WORKOUT_COLUMNS = "id, user_id, started_at, ended_at, calories"

# MET (метаболический эквивалент) по уровню тренировки
MET_BY_LEVEL: dict[str, float] = {
    "beginner": 3.5,
    "intermediate": 5.0,
    "hard": 8.0,
}
DEFAULT_LEVEL = "intermediate"
