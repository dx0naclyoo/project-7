from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=18, description="Имя пользователя")
    password: str = Field(min_length=6, max_length=72, description="Пароль")


class UserLogin(BaseModel):
    username: str = Field(min_length=1, max_length=18)
    password: str = Field(min_length=1, max_length=72)


class UserResponse(BaseModel):
    id: int
    username: str


class SessionResponse(BaseModel):
    token: str
    expires_at: datetime
    user: UserResponse
