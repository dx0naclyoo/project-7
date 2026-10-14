from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=18, description="Имя пользователя")


class UserResponse(BaseModel):
    id: int
    username: str