from app.database import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import Column, String, Date, Integer, ForeignKey


class User(Base):
    __tablename__ = "user"

    id = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    user_name = Column(String)
    email = Column(String)
    join_date = Column(Date, default=datetime.now(timezone.utc).date)
    last_login = Column(Date, default=datetime.now(timezone.utc).date)

    # Relationships
    samples = relationship("Sample", back_populates="creator")
    groups = relationship("Group", secondary="membership", back_populates="users")

    def serialize(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "user_name": self.user_name,
            "email": self.email,
            "join_date": self.join_date,
            "last_login": self.last_login,
        }


class Group(Base):
    __tablename__ = "group"

    class GroupType(Enum):
        USER = 0
        ORGANIZATION = 1

    id = Column(String, primary_key=True)
    type = Column(SQLAlchemyEnum(GroupType))
    description = Column(String)

    # Relationships
    users = relationship("User", secondary="membership", back_populates="groups")
    sites = relationship("Site", back_populates="permission_group")
    records = relationship("Record", secondary="ownership", back_populates="groups")

    def serialize(self):
        return {"id": self.id, "type": self.type, "description": self.description}


class Membership(Base):
    __tablename__ = "membership"

    user_id = Column(String, ForeignKey("user.id"), primary_key=True)
    group_id = Column(String, ForeignKey("group.id"), primary_key=True)


class Site(Base):
    __tablename__ = "site"

    id = Column(String, primary_key=True)
    permission = Column(String, ForeignKey("group.id"))
    created_date = Column(Date, default=datetime.now(timezone.utc).date)
    gps_longitude = Column(Integer)
    gps_latitude = Column(Integer)
    description = Column(String)

    # Relationships
    permission_group = relationship("Group", back_populates="sites")
    records = relationship("Record", back_populates="site")

    def serialize(self):
        return {
            "id": self.id,
            "permission": self.permission,
            "created_data": self.created_data,
            "gps_longitude": self.gps_longitude,
            "gps_latitude": self.gps_latitude,
            "description": self.description,
        }


class Record(Base):
    __tablename__ = "record"

    id = Column(String, primary_key=True)
    site_id = Column(String, ForeignKey("site.id"))
    created_date = Column(Date, default=datetime.now(timezone.utc).date)
    created_by = Column(String, ForeignKey("user.id"))

    # Relationships
    site = relationship("Site", back_populates="records")
    samples = relationship("Sample", back_populates="record")
    groups = relationship("Group", secondary="ownership", back_populates="records")

    def serialize(self):
        return {
            "id": self.id,
            "site_id": self.site_id,
            "created_data": self.created_data,
        }


class Ownership(Base):
    __tablename__ = "ownership"

    group_id = Column(String, ForeignKey("group.id"), primary_key=True)
    record_id = Column(String, ForeignKey("record.id"), primary_key=True)


class Sample(Base):
    __tablename__ = "sample"

    id = Column(String, primary_key=True)
    record_id = Column(String, ForeignKey("record.id"))
    created_date = Column(Date, default=datetime.now(timezone.utc).date)
    created_by = Column(String, ForeignKey("user.id"))
    image_url = Column(String)
    type = Column(String)
    processing_status = Column(String)

    # Relationships
    record = relationship("Record", back_populates="samples")
    creator = relationship("User", back_populates="samples")
    masks = relationship("Mask", back_populates="sample")
    bounding_boxes = relationship("BoundingBox", back_populates="sample")

    def serialize(self):
        return {
            "id": self.id,
            "record_id": self.record_id,
            "created_date": self.created_date,
            "created_by": self.created_by,
            "image_url": self.image_url,
            "type": self.type,
            "processing_status": self.processing_status,
        }


class Mask(Base):
    __tablename__ = "mask"

    sample_id = Column(String, ForeignKey("sample.id"), primary_key=True)
    mask = Column(String)
    label = Column(String)
    confidence = Column(String)

    # Relationships
    sample = relationship("Sample", back_populates="masks")

    def serialize(self):
        return {"sample_id": self.sample_id, "mask": self.mask}


class BoundingBox(Base):
    __tablename__ = "bounding_box"

    sample_id = Column(String, ForeignKey("sample.id"), primary_key=True)
    box = Column(String)
    label = Column(String)
    confidence = Column(String)

    # Relationships
    sample = relationship("Sample", back_populates="bounding_boxes")

    def serialize(self):
        return {"sample_id": self.sample_id, "box": self.box}
