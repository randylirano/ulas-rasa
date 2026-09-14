from uuid import UUID

from fastapi import APIRouter

from app.models.user import CreateUser, User
from app.services import users as service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{id}", response_model=User)
async def get_user(id: UUID):
    return await service.get_user_by_id(id=id)


@router.post("/")
async def create_user(create_user: CreateUser):
    return await service.create_user(data=create_user)
