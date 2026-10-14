from fastapi import APIRouter, HTTPException

from src.db import Connection
from src.goals.schemas import GoalCreate, GoalResponse

router = APIRouter(prefix="/users/goals", tags=["goals"])


@router.post("/", status_code=201, response_model=GoalResponse)
async def set_goal(data: GoalCreate, conn: Connection) -> GoalResponse:
    user = await conn.fetchrow("SELECT id FROM users WHERE id = $1", data.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    row = await conn.fetchrow(
        "INSERT INTO goals (user_id, goal_type, target_weight) "
        "VALUES ($1, $2, $3) "
        "ON CONFLICT (user_id) DO UPDATE "
        "SET goal_type = EXCLUDED.goal_type, target_weight = EXCLUDED.target_weight "
        "RETURNING id, user_id, goal_type, target_weight",
        data.user_id,
        data.goal_type.value,
        data.target_weight,
    )
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to save goal")
    return GoalResponse(**dict(row))


@router.get("/{user_id}", response_model=GoalResponse)
async def get_goal(user_id: int, conn: Connection) -> GoalResponse:
    row = await conn.fetchrow(
        "SELECT id, user_id, goal_type, target_weight FROM goals WHERE user_id = $1",
        user_id,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return GoalResponse(**dict(row))