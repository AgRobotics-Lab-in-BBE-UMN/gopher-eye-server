from typing import List
from app.models import Group, Ownership, User, db, Record


class RecordRepository:
    @staticmethod
    def get_by_id(record_id: str) -> Record:
        return db.session.query(Record).filter(Record.id == record_id).first()

    @staticmethod
    def get_by_group_id(group_id: str) -> List[Record]:
        return (
            db.session.query(Record)
            .join(Ownership, Ownership.record_id == Record.id)
            .join(Group, Ownership.group_id == Group.id)
            .filter(Group.id == group_id)
            .all()
        )

    @staticmethod
    def create(record: Record, owner: Group) -> Record:
        ownership = Ownership(record_id=record.id, group_id=owner.id)
        db.session.add_all([record, ownership])
        db.session.commit()
        return record

    @staticmethod
    def update(record: Record) -> Record:
        db.session.commit()
        return record

    @staticmethod
    def delete(record: Record) -> None:
        db.session.delete(record)
        db.session.commit()
        return record
