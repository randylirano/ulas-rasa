from psycopg_pool import AsyncConnectionPool
from app.config import settings

pool = AsyncConnectionPool(
    conninfo=settings.database_url,
    min_size=1,
    max_size=10,
    open=False
)