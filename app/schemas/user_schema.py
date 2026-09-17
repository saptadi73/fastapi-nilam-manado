from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from app.models.user import UserRole


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = None
    name: str
    email: str
    password: str
    role: UserRole


class UserResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    role: UserRole


class UserRefSchema(BaseModel):
    id: UUID
    name: Optional[str] = None
    email: Optional[str] = None
