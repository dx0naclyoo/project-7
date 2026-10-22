from fastapi import APIRouter

from src.db import Connection
from src.goals.schemas import GoalCreate, GoalResponse
from src.goals.service import GoalService

router = APIRouter(prefix="/users/goals", tags=["goals"])


@router.post("/", status_code=201, response_model=GoalResponse)
async def set_goal(data: GoalCreate, conn: Connection) -> GoalResponse:
    return await GoalService(conn).set_goal(data)


@router.get("/{user_id}", response_model=GoalResponse)
async def get_goal(user_id: int, conn: Connection) -> GoalResponse:
    return await GoalService(conn).get_goal(user_id)
