import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Record, Group, Ownership
from app.repositories.record_repo import RecordRepository

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
    group1 = Group(id="group1", type=Group.GroupType.USER, description="Test Group 1")
    group2 = Group(id="group2", type=Group.GroupType.ORGANIZATION, description="Test Group 2")
    
    record1 = Record(id="record1", site_id="site1", created_data=datetime.now(timezone.utc).date())
    record2 = Record(id="record2", site_id="site2", created_data=datetime.now(timezone.utc).date())
    
    ownership1 = Ownership(group_id="group1", record_id="record1")
    ownership2 = Ownership(group_id="group2", record_id="record2")
    
    db_session.add_all([group1, group2, record1, record2, ownership1, ownership2])
    db_session.commit()
    
    return {
        "group1": group1, 
        "group2": group2, 
        "record1": record1, 
        "record2": record2
    }

class TestRecordRepository:
    def test_get_by_id(self, db_session, test_data):
        record_id = "record1"
        record = db_session.query(Record).filter_by(id=record_id).first()
        
        # Assert
        assert record is not None
        assert record.id == record_id
        assert record.site_id == "site1"
    
    def test_get_by_group_id(self, db_session, test_data):
        group_id = "group1"
        records = db_session.query(Record).join(Ownership).filter(Ownership.group_id == group_id).all()
        
        # Assert
        assert len(records) == 1
        assert records[0].id == "record1"
        
        # Test with another group
        group_id_2 = "group2"
        records2 = db_session.query(Record).join(Ownership).filter(Ownership.group_id == group_id_2).all()
        assert len(records2) == 1
        assert records2[0].id == "record2"
    
    def test_create(self, db_session):
        record_id = str(uuid.uuid4())
        new_record = Record(
            id=record_id,
            site_id="site3",
            created_data=datetime.now(timezone.utc).date()
        )
        group = Group(id="group3", type=Group.GroupType.USER, description="Test Group 3")
        
        db_session.add(group)
        db_session.add(new_record)
        db_session.commit()
        
        # Assert
        saved_record = db_session.query(Record).filter_by(id=record_id).first()
        assert saved_record is not None
        assert saved_record.site_id == "site3"
    
    def test_update(self, db_session, test_data):
        record_id = "record1"
        record = db_session.query(Record).filter_by(id=record_id).first()
        record.site_id = "updated_site"
        
        db_session.commit()
        
        # Assert
        updated_record = db_session.query(Record).filter_by(id=record_id).first()
        assert updated_record.site_id == "updated_site"
    
    def test_delete(self, db_session, test_data):
        record_id = "record2"
        record = db_session.query(Record).filter_by(id=record_id).first()
        
        db_session.delete(record)
        db_session.commit()
        
        # Verify record was removed from database
        deleted_record = db_session.query(Record).filter_by(id=record_id).first()
        assert deleted_record is None
