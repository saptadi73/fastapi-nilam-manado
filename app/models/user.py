import uuid
from enum import Enum

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    OFFICER = "OFFICER"
    USER = "USER"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    role = Column(String(20), nullable=False, default=UserRole.ADMIN.value, server_default=UserRole.ADMIN.value)
