from fastapi import FastAPI,Depends,HTTPException
from pydantic import BaseModel, Field
from enum import Enum
app = FastAPI()
from src.db import get_connection
from decimal import Decimal
import asyncpg


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


@app.post("/users/parameters/", status_code=201, response_model=UserParametersResponse)
async def create_parameters(
    data: UserParametersCreate,
    conn: asyncpg.Connection = Depends(get_connection),
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
    return UserParametersResponse(**dict(row))