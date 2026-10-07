from collections.abc import AsyncIterator

import asyncpg

DATABASE_URL = "postgresql://user:password@localhost:5432/mydb"


async def get_connection() -> AsyncIterator[asyncpg.Connection]:
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()