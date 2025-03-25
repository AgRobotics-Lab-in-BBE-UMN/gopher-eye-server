import pytest
import uuid
from datetime import datetime, timezone
from app.models import db, Group, Membership, User
from app.repositories.group_repo import GroupRepository
from app.router import create_api
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
def test_data(database):
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

    group1 = Group(id="group1", type="USER", description="Test Group 1")
    group2 = Group(id="group2", type="ORGANIZATION", description="Test Group 2")

    membership1 = Membership(user_id="user1", group_id="group1")
    membership2 = Membership(user_id="user2", group_id="group2")

    db.session.add_all([user1, user2, group1, group2, membership1, membership2])
    db.session.commit()

    return {"user1": user1, "user2": user2, "group1": group1, "group2": group2}

class TestGroupRepository:
    def test_get_by_user_id(self, database, test_data):
        groups_user1 = GroupRepository.get_by_user_id("user1")
        groups_user2 = GroupRepository.get_by_user_id("user2")

        # Assert
        assert len(groups_user1) == 1
        assert groups_user1[0].id == "group1"
        assert groups_user1[0].description == "Test Group 1"

        assert len(groups_user2) == 1
        assert groups_user2[0].id == "group2"
        assert groups_user2[0].description == "Test Group 2"

    def test_create_group(self, database):
        new_group = GroupRepository.create_group(Group.GroupType.USER, "New Test Group")

        # Assert
        assert new_group is not None
        assert new_group.type == Group.GroupType.USER
        assert new_group.description == "New Test Group"

        # Verify group was saved to the database
        saved_group = Group.query.get(new_group.id)
        assert saved_group is not None
        assert saved_group.type == Group.GroupType.USER
        assert saved_group.description == "New Test Group"

    def test_create_user_group(self, database, test_data):
        user = test_data["user1"]

        membership = GroupRepository.create_user_group(user)

        # Assert
        assert membership is not None
        assert membership.user_id == user.id

        saved_membership = Membership.query.filter_by(user_id=user.id).first()
        assert saved_membership is not None
        assert saved_membership.group_id is not None

        saved_group = Group.query.get(saved_membership.group_id)
        assert saved_group is not None
        assert saved_group.type == Group.GroupType.USER
        assert saved_group.description == "User Group"