from typing import List
from sqlalchemy.orm import Session
from app.models import Group, Ownership, Record


class RecordRepository:
    @staticmethod
    def get_by_id(db: Session, record_id: str) -> Record:
        return db.query(Record).filter(Record.id == record_id).first()

    @staticmethod
    def get_by_group_id(db: Session, group_id: str) -> List[Record]:
        return (
            db.query(Record)
            .join(Ownership, Ownership.record_id == Record.id)
            .filter(Ownership.group_id == group_id)
            .all()
        )

    @staticmethod
    def create(db: Session, record: Record, group: Group) -> Record:
        ownership = Ownership(record_id=record.id, group_id=group.id)
        db.add(record)
        db.commit()
        db.add(ownership)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def update(db: Session, record: Record) -> Record:
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def delete(db: Session, record: Record) -> None:
        db.delete(record)
        db.commit()
