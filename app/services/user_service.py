# Contoh service logic
from app.models.user import User
from typing import List
from sqlalchemy.orm import Session

def get_users(db: Session) -> List[User]:
    return db.query(User).all()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_data: dict):
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
