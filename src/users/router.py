from fastapi import APIRouter

from src.db import Connection
from src.users.schemas import UserCreate, UserResponse
from src.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=201, response_model=UserResponse)
async def create_user(data: UserCreate, conn: Connection) -> UserResponse:
    return await UserService(conn).create(data)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, conn: Connection) -> None:
    await UserService(conn).delete(user_id)
