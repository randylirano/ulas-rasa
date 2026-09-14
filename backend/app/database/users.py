from uuid import UUID

from psycopg.rows import dict_row

from app.database.connection import pool
from app.models import user


async def get_user_by_id(id: UUID) -> dict | None:
    async with (
        pool.connection() as conn,
        conn.cursor(row_factory=dict_row) as cur,
    ):
        await cur.execute(
            """
            SELECT u.*
            FROM users u
            WHERE u.id = %s
            """,
            (id,),
        )
        return await cur.fetchone()


# Create a single user entry into the DB
async def create_user(data: user.CreateUser) -> UUID:
    async with (
        pool.connection() as conn,
        conn.cursor() as cur,
    ):
        await cur.execute(
            """
            INSERT INTO users (first_name, middle_name, last_name, email, password_hash)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                data.first_name,
                data.middle_name,
                data.last_name,
                data.email,
                data.password_hash,
            ),
        )
        row = await cur.fetchone()

        if row is None:
            raise RuntimeError("Insert did not return a row")

        return row[0]
