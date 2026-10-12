from fastapi import APIRouter, HTTPException

from src.db import Connection
from src.users.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=201, response_model=UserResponse)
async def create_user(data: UserCreate, conn: Connection) -> UserResponse:
    row = await conn.fetchrow(
        "INSERT INTO users (username) VALUES ($1) RETURNING id, username",
        data.username,
    )
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create user")
    return UserResponse(**dict(row))


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, conn: Connection) -> None:
    async with conn.transaction():
        await conn.execute("DELETE FROM goals WHERE user_id = $1", user_id)
        await conn.execute("DELETE FROM parameters WHERE user_id = $1", user_id)
        deleted = await conn.fetchrow(
            "DELETE FROM users WHERE id = $1 RETURNING id", user_id
        )
    if deleted is None:
        raise HTTPException(status_code=404, detail="User not found")