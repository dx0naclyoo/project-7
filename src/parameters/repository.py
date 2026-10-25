import asyncpg

from src.parameters.schemas import UserParametersCreate, UserParametersResponse


class ParametersRepository:
    def __init__(self, conn: asyncpg.Connection) -> None:
        self.conn = conn

    async def upsert(self, data: UserParametersCreate) -> UserParametersResponse | None:
        row = await self.conn.fetchrow(
    """
            INSERT INTO parameters (user_id, gender, age, weight, height)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id) DO UPDATE SET
            gender = EXCLUDED.gender,
            age = EXCLUDED.age,
            weight = EXCLUDED.weight,
            height = EXCLUDED.height
            RETURNING id, user_id, gender, age, weight, height
        """,
            data.user_id,
            data.gender.value,
            data.age,
            data.weight,
            data.height,
        )
        return UserParametersResponse(**dict(row)) if row else None

    async def get(self, user_id: int) -> UserParametersResponse | None:
        row = await self.conn.fetchrow(
            "SELECT id, user_id, gender, age, weight, height "
            "FROM parameters WHERE user_id = $1",
            user_id,
        )
        return UserParametersResponse(**dict(row)) if row else None
