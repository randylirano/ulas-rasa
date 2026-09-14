import uuid

from pydantic import BaseModel


class CreateUser(BaseModel):
    first_name: str
    middle_name: str | None = None
    last_name: str
    email: str
    password_hash: str


class User(BaseModel):
    id: uuid.UUID
    first_name: str
    middle_name: str | None = None
    last_name: str
    email: str
