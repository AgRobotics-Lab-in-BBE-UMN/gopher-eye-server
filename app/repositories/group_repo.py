import uuid
from app.models import Group, Membership, db, User
from typing import List

class GroupRepository:
    @staticmethod
    def get_by_user_id(user_id: str) -> List[Group]:
        return db.session.query(Group).join(Membership).filter(Membership.user_id == user_id).all()
    
    @staticmethod
    def create_group(type: Group.GroupType, description: str) -> Group:
        group = Group()
        group.id = str(uuid.uuid4())
        group.type = type
        group.description = description
        
        db.session.add(group)
        db.session.commit()
        return group

    @staticmethod
    def create_user_group(user: User) -> Membership:
        group = GroupRepository.create_group(Group.GroupType.USER, f"User Group")
        membership = Membership(user_id=user.id, group_id=group.id)
        db.session.add(membership)
        db.session.commit()
        return membership
    
    