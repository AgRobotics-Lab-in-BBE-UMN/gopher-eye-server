import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Group, Membership
from app.repositories.user_repo import UserRepository

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_users(db_session):
    user1 = User(
        id="user1", 
        first_name="John", 
        last_name="Doe", 
        user_name="johndoe",
        join_date=datetime.now(timezone.utc).date()
    )
    user2 = User(
        id="user2", 
        first_name="Jane", 
        last_name="Smith", 
        user_name="janesmith",
        join_date=datetime.now(timezone.utc).date()
    )
    
    group1 = Group(id="group1", type=Group.GroupType.USER, description="Admin Group")
    
    membership1 = Membership(user_id="user1", group_id="group1")
    
    # db_session.add_all([user1, user2, group1, membership1])
    db_session.add_all([user1, user2])
    db_session.commit()
    
    return {"user1": user1, "user2": user2, "group1": group1}

class TestUserRepository:
    def test_get_by_id(self, db_session, test_users):
        user_id = "user1"
        
        user = db_session.query(User).filter_by(id=user_id).first()
        
        assert user is not None
        assert user.id == user_id
        assert user.first_name == "John"
        assert user.last_name == "Doe"
    
    def test_get_all(self, db_session, test_users):
        users = db_session.query(User).all()
        
        # Assert
        assert len(users) == 2
        assert any(u.id == "user1" for u in users)
        assert any(u.id == "user2" for u in users)
    
    def test_create(self, db_session):
        user_id = str(uuid.uuid4())
        user_data = {
            'id': user_id,
            'first_name': 'New',
            'last_name': 'User',
            'user_name': 'newuser'
        }
        
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        
        # Assert
        saved_user = db_session.query(User).filter_by(id=user_id).first()
        assert saved_user is not None
        assert saved_user.first_name == 'New'
        assert saved_user.last_name == 'User'
    
    def test_update(self, db_session, test_users):
        user_id = "user1"
        user = db_session.query(User).filter_by(id=user_id).first()
        user.first_name = 'Updated'
        user.last_name = 'Name'
        
        db_session.commit()
        
        # Assert
        updated_user = db_session.query(User).filter_by(id=user_id).first()
        assert updated_user.first_name == 'Updated'
        assert updated_user.last_name == 'Name'
        assert updated_user.user_name == 'johndoe'  # Unchanged field
    
    def test_delete(self, db_session, test_users):
        user_id = "user2"
        user = db_session.query(User).filter_by(id=user_id).first()
        
        db_session.delete(user)
        db_session.commit()
        
        # Verify user was removed from database
        deleted_user = db_session.query(User).filter_by(id=user_id).first()
        assert deleted_user is None
    
    def test_get_all_users(self, db_session, test_users):
        users = db_session.query(User).all()
        
        # Assert
        assert len(users) == 2
        assert any(u.id == "user1" for u in users)
        assert any(u.id == "user2" for u in users)
