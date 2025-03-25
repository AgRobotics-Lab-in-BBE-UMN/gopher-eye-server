from app.models import db, User
from typing import List

class UserRepository:
    @staticmethod
    def get_by_id(user_id : str) -> User:
        return db.session.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(email: str) -> User:
        return db.session.query(User).filter(User.email == email).first()

    @staticmethod
    def create(user: User) -> User:
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update(user: User) -> User:
        db.session.commit()
        return user

    @staticmethod
    def delete(user: User) -> None:
        db.session.delete(user)
        db.session.commit()
        return user

    @staticmethod
    def get_all_users() -> List[User]:
        return db.session.query(User).all()
