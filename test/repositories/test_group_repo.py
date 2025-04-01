import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Group, Membership, User
from app.repositories.group_repo import GroupRepository

# Create a test database engine
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
def test_data(db_session):
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

    group1 = Group(id="group1", type=Group.GroupType.USER, description="Test Group 1")
    group2 = Group(id="group2", type=Group.GroupType.ORGANIZATION, description="Test Group 2")

    membership1 = Membership(user_id="user1", group_id="group1")
    membership2 = Membership(user_id="user2", group_id="group2")

    db_session.add_all([user1, user2, group1, group2, membership1, membership2])
    db_session.commit()

    return {"user1": user1, "user2": user2, "group1": group1, "group2": group2}

class TestGroupRepository:
    def test_get_by_user_id(self, db_session, test_data):
        user1_id = "user1"
        user2_id = "user2"

        groups_user1 = db_session.query(Group).join(Membership).filter(Membership.user_id == user1_id).all()
        groups_user2 = db_session.query(Group).join(Membership).filter(Membership.user_id == user2_id).all()

        # Assert
        assert len(groups_user1) == 1
        assert groups_user1[0].id == "group1"
        assert groups_user1[0].description == "Test Group 1"

        assert len(groups_user2) == 1
        assert groups_user2[0].id == "group2"
        assert groups_user2[0].description == "Test Group 2"

    def test_create_group(self, db_session):
        group_id = str(uuid.uuid4())
        new_group = Group(
            id=group_id,
            type=Group.GroupType.USER,
            description="New Test Group"
        )
        db_session.add(new_group)
        db_session.commit()

        # Assert
        saved_group = db_session.query(Group).filter_by(id=group_id).first()
        assert saved_group is not None
        assert saved_group.type == Group.GroupType.USER
        assert saved_group.description == "New Test Group"

    def test_create_user_group(self, db_session, test_data):
        user = test_data["user1"]

        group_id = str(uuid.uuid4())
        new_group = Group(
            id=group_id,
            type=Group.GroupType.USER,
            description="User Group"
        )
        db_session.add(new_group)

        membership = Membership(user_id=user.id, group_id=group_id)
        db_session.add(membership)
        db_session.commit()

        # Assert
        saved_membership = db_session.query(Membership).filter_by(user_id=user.id).first()
        assert saved_membership is not None
        assert saved_membership.group_id == group_id

        saved_group = db_session.query(Group).filter_by(id=group_id).first()
        assert saved_group is not None
        assert saved_group.type == Group.GroupType.USER
        assert saved_group.description == "User Group"