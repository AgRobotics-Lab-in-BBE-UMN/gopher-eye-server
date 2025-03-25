from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    user_name = db.Column(db.String)
    join_date = db.Column(db.Date, default=datetime.now(timezone.utc).date)
    last_login = db.Column(db.Date, default=datetime.now(timezone.utc).date)
    
    # Relationships
    samples = relationship("Sample", back_populates="creator")
    groups = relationship("Group", secondary="membership", back_populates="users")
    
    def serialize(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'user_name': self.user_name,
            'join_date': self.join_date,
            'last_login': self.last_login
        }


class Group(db.Model):
    __tablename__ = "group"
    
    class GroupType(Enum):
        USER = 0
        ORGANIZATION = 1
    
    id = db.Column(db.String, primary_key=True)
    type = db.Column(SQLAlchemyEnum(GroupType))
    description = db.Column(db.String)
    
    # Relationships
    users = relationship("User", secondary="membership", back_populates="groups")
    sites = relationship("Site", back_populates="permission_group")
    records = relationship("Record", secondary="ownership", back_populates="groups")
    
    def serialize(self):
        return {
            'id': self.id,
            'type': self.type,
            'description': self.description
        }


class Membership(db.Model):
    __tablename__ = "membership"
    
    user_id = db.Column(db.String, db.ForeignKey('user.id'), primary_key=True)
    group_id = db.Column(db.String, db.ForeignKey('group.id'), primary_key=True)


class Site(db.Model):
    __tablename__ = "site"
    
    id = db.Column(db.String, primary_key=True)
    permission = db.Column(db.String, db.ForeignKey('group.id'))
    creation_date = db.Column(db.Date, default=datetime.now(timezone.utc).date)
    gps_longitude = db.Column(db.Integer)
    gps_latitude = db.Column(db.Integer)
    description = db.Column(db.String)
    
    # Relationships
    permission_group = relationship("Group", back_populates="sites")
    records = relationship("Record", back_populates="site")
    
    def serialize(self):
        return {
            'id': self.id,
            'permission': self.permission,
            'creation_date': self.creation_date,
            'gps_longitude': self.gps_longitude,
            'gps_latitude': self.gps_latitude,
            'description': self.description
        }


class Record(db.Model):
    __tablename__ = "record"
    
    id = db.Column(db.String, primary_key=True)
    site_id = db.Column(db.String, db.ForeignKey('site.id'))
    creation_date = db.Column(db.Date, default=datetime.now(timezone.utc).date)
    created_by = db.Column(db.String, db.ForeignKey('user.id'))
    
    # Relationships
    site = relationship("Site", back_populates="records")
    samples = relationship("Sample", back_populates="record")
    groups = relationship("Group", secondary="ownership", back_populates="records")
    
    def serialize(self):
        return {
            'id': self.id,
            'site_id': self.site_id,
            'creation_date': self.creation_date
        }


class Ownership(db.Model):
    __tablename__ = "ownership"
    
    group_id = db.Column(db.String, db.ForeignKey('group.id'), primary_key=True)
    record_id = db.Column(db.String, db.ForeignKey('record.id'), primary_key=True)


class Sample(db.Model):
    __tablename__ = "sample"
    
    id = db.Column(db.String, primary_key=True)
    record_id = db.Column(db.String, db.ForeignKey('record.id'))
    created_date = db.Column(db.Date, default=datetime.now(timezone.utc).date)
    created_by = db.Column(db.String, db.ForeignKey('user.id'))
    image_url = db.Column(db.String)
    type = db.Column(db.String)
    processing_status = db.Column(db.String)
    
    # Relationships
    record = relationship("Record", back_populates="samples")
    creator = relationship("User", back_populates="samples")
    masks = relationship("Mask", back_populates="sample")
    bounding_boxes = relationship("BoundingBox", back_populates="sample")
    
    def serialize(self):
        return {
            'id': self.id,
            'record_id': self.record_id,
            'created_date': self.created_date,
            'created_by': self.created_by,
            'image_url': self.image_url,
            'type': self.type,
            'processing_status': self.processing_status
        }


class Mask(db.Model):
    __tablename__ = "mask"
    
    image_id = db.Column(db.String, db.ForeignKey('sample.id'), primary_key=True)
    mask = db.Column(db.String)
    
    # Relationships
    sample = relationship("Sample", back_populates="masks")
    
    def serialize(self):
        return {
            'image_id': self.image_id,
            'mask': self.mask
        }


class BoundingBox(db.Model):
    __tablename__ = "bounding_box"
    
    image_id = db.Column(db.String, db.ForeignKey('sample.id'), primary_key=True)
    box = db.Column(db.String)
    
    # Relationships
    sample = relationship("Sample", back_populates="bounding_boxes")
    
    def serialize(self):
        return {
            'image_id': self.image_id,
            'box': self.box
        }
