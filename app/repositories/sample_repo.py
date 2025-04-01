from typing import List
from sqlalchemy.orm import Session
from app.models import Group, Ownership, Sample, Record

class SampleRepository:
    @staticmethod
    def get_by_id(db: Session, sample_id: str) -> Sample:
        """Retrieve a sample by its ID."""
        return db.query(Sample).filter(Sample.id == sample_id).first()

    @staticmethod
    def get_by_record_id(db: Session, record_id: str) -> List[Sample]:
        """Retrieve all samples associated with a specific record."""
        return db.query(Sample).filter(Sample.record_id == record_id).all()

    @staticmethod
    def get_by_owner_id(db: Session, group: Group) -> List[Sample]:
        """Retrieve all samples for a given owner."""
        return (
            db.query(Sample)
            .join(Record, Sample.record_id == Record.id)
            .join(Ownership, Ownership.record_id == Record.id)
            .filter(Ownership.group_id == group.id)
            .all()
        )

    @staticmethod
    def create(db: Session, sample: Sample) -> Sample:
        """Create a new sample."""
        db.add(sample)
        db.commit()
        db.refresh(sample)
        return sample

    @staticmethod
    def update(db: Session, sample: Sample) -> Sample:
        """Update an existing sample."""
        db.commit()
        db.refresh(sample)
        return sample

    @staticmethod
    def delete(db: Session, sample: Sample) -> None:
        """Delete a sample."""
        db.delete(sample)
        db.commit()