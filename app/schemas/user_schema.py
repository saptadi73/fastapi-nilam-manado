from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = None
    name: str
    email: str
    password: str = None


class UserRefSchema(BaseModel):
    id: UUID
    name: Optional[str] = None
    email: Optional[str] = None
