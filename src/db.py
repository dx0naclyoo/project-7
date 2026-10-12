import os
from collections.abc import AsyncIterator
from typing import Annotated

import asyncpg
from dotenv import load_dotenv
from fastapi import Depends

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


async def get_connection() -> AsyncIterator[asyncpg.Connection]:
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()


Connection = Annotated[asyncpg.Connection, Depends(get_connection)]



