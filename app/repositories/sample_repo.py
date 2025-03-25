from typing import List
from app.models import Group, Ownership, db, Sample, Record, User


class SampleRepository:
    @staticmethod
    def get_by_id(sample_id: str) -> Sample:
        """Retrieve a sample by its ID."""
        return db.session.query(Sample).filter(Sample.id == sample_id).first()

    @staticmethod
    def get_by_record_id(record_id: str) -> List[Sample]:
        """Retrieve all samples associated with a specific record."""
        return db.session.query(Sample).filter(Sample.record_id == record_id).all()

    @staticmethod
    def get_by_owner_id(group: Group) -> List[Sample]:
        """Retrieve all samples for a given owner."""
        return (
            db.session.query(Sample)
            .join(Record, Sample.record_id == Record.id)
            .join(Ownership, Ownership.record_id == Record.id)
            .filter(Group.id == group.id)
            .all()
        )

    @staticmethod
    def create(sample: Sample) -> Sample:
        """Create a new sample."""
        db.session.add(sample)
        db.session.commit()
        return sample

    @staticmethod
    def update(sample: Sample) -> Sample:
        """Update an existing sample."""
        db.session.commit()
        return sample

    @staticmethod
    def delete(sample: Sample) -> None:
        """Delete a sample."""
        db.session.delete(sample)
        db.session.commit()