import asyncpg

from src.parameters.schemas import UserParametersCreate, UserParametersResponse


class ParametersRepository:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.conn = conn

    async def create(self, data: UserParametersCreate) -> UserParametersResponse | None:
        row = await self.conn.fetchrow(
            "INSERT INTO parameters (user_id, gender, age, weight) "
            "VALUES ($1, $2, $3, $4) "
            "RETURNING id, user_id, gender, age, weight",
            data.user_id,
            data.gender.value,
            data.age,
            data.weight,
        )
        return UserParametersResponse(**dict(row)) if row else None
