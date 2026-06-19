import psycopg_pool
from app.config import settings

pool: psycopg_pool.AsyncConnectionPool | None = None

async def get_pool() -> psycopg_pool.AsyncConnectionPool:
    global pool
    if pool is None:
        pool = psycopg_pool.AsyncConnectionPool(
            conninfo=settings.database_url,
            min_size=1,
            max_size=10,
            open=False
        )
    await pool.open(wait=True, timeout=10)
    return pool


async def get_connection():
    p = await get_pool()
    return p.connection()