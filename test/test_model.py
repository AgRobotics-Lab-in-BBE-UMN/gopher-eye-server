import pytest
from app.models import User, Group, Site, Record, Sample, Mask, BoundingBox
import uuid

def test_create_user(database):
    """Test user creation and retrieval"""
    user_id = str(uuid.uuid4())
    user = User(id=user_id, first_name="Test", last_name="User", user_name="testuser")
    
    database.session.add(user)
    database.session.commit()
    
    saved_user = User.query.get(user_id)
    assert saved_user is not None
    assert saved_user.first_name == "Test"
    assert saved_user.last_name == "User"
    
def test_user_serialize(database, test_data):
    """Test user serialization"""
    user = User.query.get("user1")
    serialized = user.serialize()
    
    assert serialized["id"] == "user1"
    assert serialized["first_name"] == "John"
    assert serialized["last_name"] == "Doe"
    assert serialized["user_name"] == "johndoe"
    
def test_group_relationship(database, test_data):
    """Test relationships between users and groups"""
    user = User.query.get("user1")
    group = Group.query.get("group1")
    
    assert user in group.users
    assert group in user.groups

def test_site_creation(database):
    """Test site creation with group permission"""
    group_id = str(uuid.uuid4())
    group = Group(id=group_id, type="site_admin", description="Site Admin Group")
    
    site_id = str(uuid.uuid4())
    site = Site(id=site_id, permission=group_id, description="New Test Site", 
               gps_longitude=300, gps_latitude=400)
    
    database.session.add_all([group, site])
    database.session.commit()
    
    saved_site = Site.query.get(site_id)
    assert saved_site is not None
    assert saved_site.permission == group_id
    assert saved_site.permission_group.id == group_id

def test_record_sample_relationship(database, test_data):
    """Test relationship between records and samples"""
    record = Record.query.get("record1")
    sample = Sample.query.get("sample1")
    
    assert sample in record.samples
    assert sample.record_id == "record1"
    
def test_sample_mask_bbox_relationship(database, test_data):
    """Test relationship between samples, masks and bounding boxes"""
    sample = Sample.query.get("sample1")
    
    assert len(sample.masks) == 1
    assert len(sample.bounding_boxes) == 1
    assert sample.masks[0].mask == "mask_data_base64"
    assert sample.bounding_boxes[0].box == "[10, 20, 100, 200]"

def test_record_serialize(database, test_data):
    """Test record serialization"""
    record = Record.query.get("record1")
    serialized = record.serialize()
    
    assert serialized["id"] == "record1"
    assert serialized["site_id"] == "site1"
    assert "creation_date" in serialized

def test_sample_creator_relationship(database, test_data):
    """Test relationship between samples and their creators"""
    sample = Sample.query.get("sample1")
    user = User.query.get("user1")
    
    assert sample.creator == user
    assert sample in user.samples

def test_multi_level_relationships(database, test_data):
    """Test traversing multiple relationship levels"""
    user = User.query.get("user1")
    group = Group.query.get("group1")
    site = Site.query.get("site1")
    
    # Verify we can navigate from group to sites
    assert site in group.sites
    
    # Verify we can navigate from user to groups to sites
    group_sites = [site for group in user.groups for site in group.sites]
    assert site in group_sites