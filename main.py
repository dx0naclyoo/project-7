from decimal import Decimal
from enum import Enum
from typing import Annotated

import asyncpg
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.db import get_connection

Connection = Annotated[asyncpg.Connection, Depends(get_connection)]

app = FastAPI()

class Gender(str, Enum):
    male = 'male'
    female = 'female'

class UserParametersCreate(BaseModel):
    user_id: int = Field(description="ID пользователя из таблицы users")
    gender: Gender = Field(description="Пол пользователя: male или female")
    age: int = Field(gt=0, lt=60, description="Возраст пользователя")
    weight: Decimal = Field(
        gt=0, le=150, max_digits=5, decimal_places=2, description="Вес пользователя в кг"
    )


class UserParametersResponse(BaseModel):
    id: int
    user_id: int
    gender: str
    age: int
    weight: Decimal

class GoalType(str, Enum):
    up_weight = "up_weight"
    lose_weight = "lose_weight"

class GoalCreate(BaseModel):
    user_id: int = Field(description = "ID юзера")
    goal_type: GoalType = Field(description="Цель: lose_weight, up_weight")
    target_weight: Decimal = Field(gt=0, le=120, max_digits=5, decimal_places=2, description="вес в кг")

class GoalResponse(BaseModel):
    id:int
    user_id: int
    goal_type: str
    target_weight: Decimal

@app.post("/users/goals/", status_code = 201, response_model=GoalResponse)
async def set_goal(data: GoalCreate, conn: Connection)-> GoalResponse:
    user = await conn.fetchrow("SELECT id FROM users WHERE id = $1", data.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail = "User not found")
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
        raise HTTPException(status_code=500,detail="Fail by saves goal")
    return GoalResponse(**dict(row))

@app.get("/users/goals/{user_id}", response_model=GoalResponse)
async def get_goal(user_id: int, conn: Connection) -> GoalResponse:
    row = await conn.fetchrow(
        "SELECT id, user_id, goal_type, target_weight FROM goals WHERE user_id = $1",
        user_id,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return GoalResponse(**dict(row))




@app.post("/users/parameters/", status_code=201, response_model=UserParametersResponse)
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

