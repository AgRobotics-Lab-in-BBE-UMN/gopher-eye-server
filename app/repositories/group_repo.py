import uuid
from sqlalchemy.orm import Session
from app.models import Group, Membership, User
from typing import List

class GroupRepository:
    @staticmethod
    def get_by_user_id(db: Session, user_id: str) -> List[Group]:
        return db.query(Group).join(Membership).filter(Membership.user_id == user_id).all()
    
    @staticmethod
    def create_group(db: Session, type: Group.GroupType, description: str) -> Group:
        group = Group(id=str(uuid.uuid4()), type=type, description=description)
        db.add(group)
        db.commit()
        db.refresh(group)
        return group

    @staticmethod
    def create_user_group(db: Session, user: User) -> Membership:
        group = GroupRepository.create_group(db, Group.GroupType.USER, "User Group")
        membership = Membership(user_id=user.id, group_id=group.id)
        db.add(membership)
        db.commit()
        db.refresh(membership)
        return membership
    
    @staticmethod
    def get_user_group(db: Session, user_id: str) -> Group:
        return db.query(Group).join(Membership).filter(Membership.user_id == user_id, Group.type == Group.GroupType.USER).first()

