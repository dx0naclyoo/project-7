from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class Gender(str, Enum):
    male = "male"
    female = "female"


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