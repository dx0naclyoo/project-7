from fastapi import APIRouter, HTTPException

from src.db import Connection
from src.parameters.schemas import UserParametersCreate, UserParametersResponse

router = APIRouter(prefix="/users/parameters", tags=["parameters"])


@router.post("/", status_code=201, response_model=UserParametersResponse)
async def create_parameters(
    data: UserParametersCreate,
    conn: Connection,
) -> UserParametersResponse:
    user = await conn.fetchrow("SELECT id FROM users WHERE id = $1", data.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    row = await conn.fetchrow(
        "INSERT INTO parameters (user_id, gender, age, weight) "
        "VALUES ($1, $2, $3, $4) "
        "RETURNING id, user_id, gender, age, weight",
        data.user_id,
        data.gender.value,
        data.age,
        data.weight,
    )
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to save parameters")
    return UserParametersResponse(**dict(row))