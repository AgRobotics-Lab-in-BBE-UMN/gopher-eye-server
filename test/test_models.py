from flask_sqlalchemy import SQLAlchemy
import pytest
from app.router import create_api
from app.application import Application
from app.models import db, User, Group, Site, Record, Sample, Membership, Ownership, Mask, BoundingBox
import uuid
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
def client(app):
    return app.test_client()

@pytest.fixture
def test_data(database):
    # Create test users
    user1 = User(id="user1", first_name="John", last_name="Doe", user_name="johndoe")
    user2 = User(id="user2", first_name="Jane", last_name="Smith", user_name="janesmith")
    
    # Create test groups
    group1 = Group(id="group1", type=Group.GroupType.USER, description="Admin Group")
    group2 = Group(id="group2", type=Group.GroupType.USER, description="User Group")
    
    # Create memberships
    membership1 = Membership(user_id="user1", group_id="group1")
    membership2 = Membership(user_id="user2", group_id="group2")
    
    # Create sites
    site1 = Site(id="site1", permission="group1", description="Test Site 1", 
                gps_longitude=100, gps_latitude=200)
    
    # Create records
    record1 = Record(id="record1", site_id="site1")
    
    # Create ownerships
    ownership1 = Ownership(group_id="group1", record_id="record1")
    
    # Create samples
    sample1 = Sample(id="sample1", record_id="record1", created_by="user1", 
                    image_url="/images/test.jpg", type="corn", 
                    processing_status="completed")
    
    # Create masks and bounding boxes
    mask1 = Mask(image_id="sample1", mask="mask_data_base64")
    bbox1 = BoundingBox(image_id="sample1", box="[10, 20, 100, 200]")
    
    # Add to database
    db.session.add_all([user1, user2, group1, group2, membership1, membership2,
                        site1, record1, ownership1, sample1, mask1, bbox1])
    db.session.commit()

def test_create_user(database):
    
    user_id = str(uuid.uuid4())
    user = User(id=user_id, first_name="Test", last_name="User", user_name="testuser")
    
    database.session.add(user)
    database.session.commit()
    
    saved_user = User.query.get(user_id)
    assert saved_user is not None
    assert saved_user.first_name == "Test"
    assert saved_user.last_name == "User"
    
def test_user_serialize(database, test_data):
    
    user = User.query.get("user1")
    serialized = user.serialize()
    
    assert serialized["id"] == "user1"
    assert serialized["first_name"] == "John"
    assert serialized["last_name"] == "Doe"
    assert serialized["user_name"] == "johndoe"
    
def test_membership(database, test_data):
    
    user = User.query.get("user1")
    group = Group.query.get("group1")
    
    memebrship = Membership.query.filter_by(user_id="user1", group_id="group1").all()
    
    assert len(memebrship) == 1

# def test_site_creation(database):
#     
#     group_id = str(uuid.uuid4())
#     group = Group(id=group_id, type="site_admin", description="Site Admin Group")
    
#     site_id = str(uuid.uuid4())
#     site = Site(id=site_id, permission=group_id, description="New Test Site", 
#                gps_longitude=300, gps_latitude=400)
    
#     database.session.add_all([group, site])
#     database.session.commit()
    
#     saved_site = Site.query.get(site_id)
#     assert saved_site is not None
#     assert saved_site.permission == group_id
#     assert saved_site.permission_group.id == group_id

def test_record_sample_relationship(database, test_data):
    
    record = Record.query.get("record1")
    sample = Sample.query.get("sample1")
    
    assert sample in record.samples
    assert sample.record_id == "record1"
    
def test_sample_mask_bbox_relationship(database, test_data):
    
    sample = Sample.query.get("sample1")
    
    assert len(sample.masks) == 1
    assert len(sample.bounding_boxes) == 1
    assert sample.masks[0].mask == "mask_data_base64"
    assert sample.bounding_boxes[0].box == "[10, 20, 100, 200]"

def test_record_serialize(database, test_data):
    
    record = Record.query.get("record1")
    serialized = record.serialize()
    
    assert serialized["id"] == "record1"
    assert serialized["site_id"] == "site1"
    assert "creation_date" in serialized

def test_sample_creator_relationship(database, test_data):
    
    sample = Sample.query.get("sample1")
    user = User.query.get("user1")
    
    assert sample.creator == user
    assert sample in user.samples
