import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Group, Site, Record, Sample, Membership, Ownership, Mask, BoundingBox
import uuid
from app.database import Base

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
    db_session.add_all([user1, user2, group1, group2, membership1, membership2,
                        site1, record1, ownership1, sample1, mask1, bbox1])
    db_session.commit()

def test_create_user(db_session):
    user_id = str(uuid.uuid4())
    user = User(id=user_id, first_name="Test", last_name="User", user_name="testuser")
    db_session.add(user)
    db_session.commit()
    
    saved_user = db_session.query(User).filter_by(id=user_id).first()
    assert saved_user is not None
    assert saved_user.first_name == "Test"
    assert saved_user.last_name == "User"

def test_user_serialize(db_session, test_data):
    user = db_session.query(User).filter_by(id="user1").first()
    serialized = user.serialize()
    assert serialized["id"] == "user1"
    assert serialized["first_name"] == "John"
    assert serialized["last_name"] == "Doe"
    assert serialized["user_name"] == "johndoe"

def test_membership(db_session, test_data):
    membership = db_session.query(Membership).filter_by(user_id="user1", group_id="group1").all()
    assert len(membership) == 1

def test_record_sample_relationship(db_session, test_data):
    record = db_session.query(Record).filter_by(id="record1").first()
    sample = db_session.query(Sample).filter_by(id="sample1").first()
    assert sample in record.samples
    assert sample.record_id == "record1"

def test_sample_mask_bbox_relationship(db_session, test_data):
    sample = db_session.query(Sample).filter_by(id="sample1").first()
    assert len(sample.masks) == 1
    assert len(sample.bounding_boxes) == 1
    assert sample.masks[0].mask == "mask_data_base64"
    assert sample.bounding_boxes[0].box == "[10, 20, 100, 200]"

def test_record_serialize(db_session, test_data):
    record = db_session.query(Record).filter_by(id="record1").first()
    serialized = record.serialize()
    assert serialized["id"] == "record1"
    assert serialized["site_id"] == "site1"
    assert "created_data" in serialized

def test_sample_creator_relationship(db_session, test_data):
    sample = db_session.query(Sample).filter_by(id="sample1").first()
    user = db_session.query(User).filter_by(id="user1").first()
    assert sample.creator == user
    assert sample in user.samples

