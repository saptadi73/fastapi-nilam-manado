from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User


def validate_user_update(db: Session, user_id: Optional[UUID]):
    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User update tidak ditemukan")
    return user


def serialize_user_ref(user: Optional[User]):
    if not user:
        return None
    return {"id": user.id, "name": user.name, "email": user.email}
