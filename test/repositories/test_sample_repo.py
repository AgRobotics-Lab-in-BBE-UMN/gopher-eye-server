import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Sample, Record, User
from app.repositories.sample_repo import SampleRepository

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
def test_samples(db_session):
    user = User(
        id="user1",
        first_name="John",
        last_name="Doe",
        user_name="johndoe",
        join_date=datetime.now(timezone.utc).date()
    )
    record = Record(
        id="record1",
        site_id="site1",
        created_data=datetime.now(timezone.utc).date(),
        created_by="user1"
    )
    sample1 = Sample(
        id="sample1",
        record_id="record1",
        created_date=datetime.now(timezone.utc).date(),
        created_by="user1",
        image_url="/images/sample1.jpg",
        type="corn",
        processing_status="completed"
    )
    sample2 = Sample(
        id="sample2",
        record_id="record1",
        created_date=datetime.now(timezone.utc).date(),
        created_by="user1",
        image_url="/images/sample2.jpg",
        type="wheat",
        processing_status="pending"
    )
    db_session.add_all([user, record, sample1, sample2])
    db_session.commit()
    return {"sample1": sample1, "sample2": sample2, "record": record, "user": user}

class TestSampleRepository:
    def test_get_by_id(self, db_session, test_samples):
        sample_id = "sample1"
        sample = db_session.query(Sample).filter_by(id=sample_id).first()
        
        assert sample is not None
        assert sample.id == sample_id
        assert sample.type == "corn"
        assert sample.processing_status == "completed"

    def test_get_all(self, db_session, test_samples):
        samples = db_session.query(Sample).all()
        
        # Assert
        assert len(samples) == 2
        assert any(s.id == "sample1" for s in samples)
        assert any(s.id == "sample2" for s in samples)

    def test_create(self, db_session):
        sample_id = str(uuid.uuid4())
        sample_data = {
            "id": sample_id,
            "record_id": "record1",
            "created_date": datetime.now(timezone.utc).date(),
            "created_by": "user1",
            "image_url": "/images/new_sample.jpg",
            "type": "soybean",
            "processing_status": "in_progress"
        }
        sample = Sample(**sample_data)
        db_session.add(sample)
        db_session.commit()
        
        # Assert
        saved_sample = db_session.query(Sample).filter_by(id=sample_id).first()
        assert saved_sample is not None
        assert saved_sample.type == "soybean"
        assert saved_sample.processing_status == "in_progress"

    def test_update(self, db_session, test_samples):
        sample_id = "sample1"
        sample = db_session.query(Sample).filter_by(id=sample_id).first()
        sample.type = "updated_type"
        sample.processing_status = "updated_status"
        
        db_session.commit()
        
        # Assert
        updated_sample = db_session.query(Sample).filter_by(id=sample_id).first()
        assert updated_sample.type == "updated_type"
        assert updated_sample.processing_status == "updated_status"

    def test_delete(self, db_session, test_samples):
        sample_id = "sample2"
        sample = db_session.query(Sample).filter_by(id=sample_id).first()
        
        db_session.delete(sample)
        db_session.commit()
        
        # Verify sample was removed from database
        deleted_sample = db_session.query(Sample).filter_by(id=sample_id).first()
        assert deleted_sample is None

    def test_get_all_samples(self, db_session, test_samples):
        samples = db_session.query(Sample).all()
        
        # Assert
        assert len(samples) == 2
        assert any(s.id == "sample1" for s in samples)
        assert any(s.id == "sample2" for s in samples)
