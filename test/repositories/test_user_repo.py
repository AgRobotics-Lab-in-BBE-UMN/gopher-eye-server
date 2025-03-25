import pytest
import uuid
from datetime import datetime, timezone
from app.router import create_api
from app.models import db, User, Group, Membership
from app.repositories.user_repo import UserRepository
from test.mock_application_layer import MockApplicationLayer

@pytest.fixture
def app():
    app = create_api(__name__, MockApplicationLayer(), instance_relative_config=True)
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def database(app):
    with app.app_context():
        yield db

@pytest.fixture
def test_users(database):
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
    
    group1 = Group(id="group1", type="admin", description="Admin Group")
    
    membership1 = Membership(user_id="user1", group_id="group1")
    
    db.session.add_all([user1, user2, group1, membership1])
    db.session.commit()
    
    return {"user1": user1, "user2": user2, "group1": group1}

class TestUserRepository:
    def test_get_by_id(self, database, test_users):
        user_id = "user1"
        
        user = UserRepository.get_by_id(user_id)
        
        assert user is not None
        assert user.id == user_id
        assert user.first_name == "John"
        assert user.last_name == "Doe"
    
    def test_get_all(self, database, test_users):
        users = UserRepository.get_all_users()
        
        # Assert
        assert len(users) == 2
        assert any(u.id == "user1" for u in users)
        assert any(u.id == "user2" for u in users)
    
    def test_create(self, database):
        user_id = str(uuid.uuid4())
        user_data = {
            'id': user_id,
            'first_name': 'New',
            'last_name': 'User',
            'user_name': 'newuser'
        }
        
        user = User(**user_data)
        
        user = UserRepository.create(user)
        
        # Assert
        assert user is not None
        assert user.id == user_id
        
        saved_user = User.query.get(user_id)
        assert saved_user is not None
        assert saved_user.first_name == 'New'
        assert saved_user.last_name == 'User'
    
    def test_update(self, database, test_users):
        user_id = "user1"
        user = UserRepository.get_by_id(user_id)
        user.first_name = 'Updated'
        user.last_name = 'Name'
        
        updated_user = UserRepository.update(user)
        
        # Assert
        assert updated_user is not None
        assert updated_user.first_name == 'Updated'
        assert updated_user.last_name == 'Name'
        assert updated_user.user_name == 'johndoe'  # Unchanged field
        
        db.session.expire_all()
        user_from_db = User.query.get(user_id)
        assert user_from_db.first_name == 'Updated'
        assert user_from_db.last_name == 'Name'
    
    def test_delete(self, database, test_users):
        user_id = "user2"
        user = UserRepository.get_by_id(user_id)
        
        UserRepository.delete(user)
        
        # Verify user was removed from database
        deleted_user = User.query.get(user_id)
        assert deleted_user is None
    
    def test_get_all_users(self, database, test_users):
        users = UserRepository.get_all_users()
        
        # Assert
        assert len(users) == 2
        assert any(u.id == "user1" for u in users)
        assert any(u.id == "user2" for u in users)
