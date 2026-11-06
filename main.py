from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.goals.router import router as goals_router
from src.parameters.router import router as parameters_router
from src.training.router import router as training_router
from src.training_days.router import router as trainings_days_router
from src.training_plan.router import router as training_plan_router
from src.users.router import router as users_router
from src.workouts.router import router as workouts_router

app = FastAPI()

app.include_router(users_router)
app.include_router(parameters_router)
app.include_router(goals_router)
app.include_router(training_router)
app.include_router(trainings_days_router)
app.include_router(workouts_router)
app.include_router(training_plan_router)


# Веб-клиент: http://localhost:8000/app/
app.mount(
    "/app",
    StaticFiles(directory=Path(__file__).parent / "web", html=True),
    name="web",
)
