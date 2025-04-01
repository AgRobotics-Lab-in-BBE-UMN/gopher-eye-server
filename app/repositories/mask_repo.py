from typing import List
from sqlalchemy.orm import Session
from app.models import Mask


class MaskRepository:
    @staticmethod
    def create(db: Session, mask: Mask) -> Mask:
        db.add(mask)
        db.commit()
        db.refresh(mask)
        return mask
    
    @staticmethod
    def get_by_sample_id(db: Session, sample_id: str) -> Mask:
        return db.query(Mask).filter(Mask.sample_id == sample_id).all()
