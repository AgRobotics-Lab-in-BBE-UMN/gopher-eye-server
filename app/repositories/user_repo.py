from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import User
from typing import List

from app.repositories.group_repo import GroupRepository

class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: str) -> User:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create(db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        GroupRepository.create_user_group(db, user)
        return user

    @staticmethod
    def update(db: Session, user: User) -> User:
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete(db: Session, user: User) -> None:
        db.delete(user)
        db.commit()

    @staticmethod
    def get_all_users(db: Session) -> List[User]:
        return db.query(User).all()
    
    @staticmethod
    def update_last_login(db: Session, user_id: str) -> User:
        user = UserRepository.get_by_id(db, user_id)
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
        return user
