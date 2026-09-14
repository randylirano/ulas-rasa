from uuid import UUID

from app.database import users
from app.models import user as userModels


async def get_user_by_id(id: UUID) -> dict | None:
    return await users.get_user_by_id(id)


async def create_user(data: userModels.CreateUser) -> UUID:
    return await users.create_user(data=data)
