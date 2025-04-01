from typing import List
from sqlalchemy.orm import Session
from app.models import BoundingBox


class BoundingBoxRepository:
    @staticmethod
    def create(db: Session, bounding_box: BoundingBox) -> BoundingBox:
        db.add(bounding_box)
        db.commit()
        db.refresh(bounding_box)
        return bounding_box
    
    @staticmethod
    def get_by_sample_id(db: Session, sample_id: str) -> BoundingBox:
        return db.query(BoundingBox).filter(BoundingBox.sample_id == sample_id).all()
