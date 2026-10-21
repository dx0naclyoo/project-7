from fastapi import FastAPI

from src.goals.router import router as goals_router
from src.parameters.router import router as parameters_router
from src.training.router import router as training_router
from src.users.router import router as users_router

app = FastAPI()

app.include_router(users_router)
app.include_router(parameters_router)
app.include_router(goals_router)
app.include_router(training_router)

@app.get("/")
def abc() -> str:
    return "make you the Best"