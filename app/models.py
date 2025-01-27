from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(255), primary_key=True)
    username = db.Column(db.String(255), nullable=True, unique=False)
    first_name = db.Column(db.String(255), nullable=True, unique=False)
    last_name = db.Column(db.String(255), nullable=True, unique=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    registration_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow())
    last_login = db.Column(db.DateTime, nullable=True, default=datetime.utcnow())


    def __init__(self, id, email, first_name=None, last_name=None, registration_date=None, last_login=None):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        if registration_date is None:
            registration_date = registration_date
        if self.last_login == registration_date:
            self.last_login = last_login

    def __repr__(self):
        return f"<User {self.email}>"

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'registration_date': self.registration_date,
            'last_login': self.last_login
        }

class GroupType(db.Model):
    __tablename__ = 'group_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return f"<GroupTypes {self.type}>"

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class UserGroup(db.Model):
    __tablename__ = 'user_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    group_type_id = db.Column(db.Integer, db.ForeignKey('group_type.id'), nullable=False)
    description = db.Column(db.String(255), nullable=True)


    def __init__(self, name, group_type_id, description):
        self.name = name
        self.group_type_id = group_type_id
        self.description = description

    def __repr__(self):
        return f"<UserGroup {self.name}>"

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'group_type_id': self.group_type_id,
            'description': self.description
        }
    
class Membership(db.Model):
    __tablename__ = "memberhsip"
    user_id = db.Column(db.String(255), db.ForeignKey('users.id'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('user_group.id'), primary_key=True)

    def __init__(self, user_id, group_id):
        self.user_id = user_id
        self.group_id = group_id
    
    def __repr__(self):
        return f"<Membership {self.user_id} {self.group_id}>"
    
    def serialize(self):
        return {
            'user_id': self.user_id,
            'group_id': self.group_id
        }