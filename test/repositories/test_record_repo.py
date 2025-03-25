import pytest
import uuid
from datetime import datetime, timezone
from app.models import db, Record, Group, Ownership
from app.repositories.record_repo import RecordRepository
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
    group1 = Group(id="group1", type="USER", description="Test Group 1")
    group2 = Group(id="group2", type="ORGANIZATION", description="Test Group 2")
    
    record1 = Record(id="record1", site_id="site1", creation_date=datetime.now(timezone.utc).date())
    record2 = Record(id="record2", site_id="site2", creation_date=datetime.now(timezone.utc).date())
    
    ownership1 = Ownership(group_id="group1", record_id="record1")
    ownership2 = Ownership(group_id="group2", record_id="record2")
    
    db.session.add_all([group1, group2, record1, record2, ownership1, ownership2])
    db.session.commit()
    
    return {
        "group1": group1, 
        "group2": group2, 
        "record1": record1, 
        "record2": record2
    }

class TestRecordRepository:
    def test_get_by_id(self, database, test_data):
        record = RecordRepository.get_by_id("record1")
        
        # Assert
        assert record is not None
        assert record.id == "record1"
        assert record.site_id == "site1"
    
    def test_get_by_group_id(self, database, test_data):
        records = RecordRepository.get_by_group_id("group1")
        
        # Assert
        assert len(records) == 1
        assert records[0].id == "record1"
        
        # Test with another group
        records2 = RecordRepository.get_by_group_id("group2")
        assert len(records2) == 1
        assert records2[0].id == "record2"
    
    def test_create(self, database, test_data):
        record_id = str(uuid.uuid4())
        new_record = Record(
            id=record_id,
            site_id="site3",
            creation_date=datetime.now(timezone.utc).date()
        )
        owner_group = Group(id="group1", type="USER", description="Test Group 1")
        
        # Act
        created_record = RecordRepository.create(new_record, owner_group)
        
        # Assert
        assert created_record is not None
        assert created_record.id == record_id
        
        # Verify record was saved to the database
        saved_record = Record.query.get(record_id)
        assert saved_record is not None
        assert saved_record.site_id == "site3"
    
    def test_update(self, database, test_data):
        record = test_data["record1"]
        record.site_id = "updated_site"
        
        # Act
        updated_record = RecordRepository.update(record)
        
        # Assert
        assert updated_record is not None
        assert updated_record.site_id == "updated_site"
        
        # Verify changes were saved to the database
        db.session.expire_all()  # Clear session cache
        saved_record = Record.query.get("record1")
        assert saved_record.site_id == "updated_site"
    
    def test_delete(self, database, test_data):
        record = test_data["record2"]
        
        # Act
        RecordRepository.delete(record)
        
        # Verify record was removed from database
        deleted_record = Record.query.get("record2")
        assert deleted_record is None
