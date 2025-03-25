import pytest
import uuid
from datetime import datetime, timezone
from app.models import db, Sample, Record, User, Group, Ownership, Mask, BoundingBox
from app.repositories.sample_repo import SampleRepository
from app.router import create_api
from test.mock_application_layer import MockApplicationLayer


@pytest.fixture
def app():
    app = create_api(__name__, MockApplicationLayer(), instance_relative_config=True)
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )

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
    user1 = User(id="user1", first_name="John", last_name="Doe", user_name="johndoe")
    group1 = Group(id="group1", type=Group.GroupType.USER, description="Test Group 1")
    record1 = Record(
        id="record1", site_id="site1", creation_date=datetime.now(timezone.utc).date()
    )
    record2 = Record(
        id="record2", site_id="site2", creation_date=datetime.now(timezone.utc).date()
    )
    ownership1 = Ownership(group_id="group1", record_id="record1")

    sample1 = Sample(
        id="sample1",
        record_id="record1",
        created_date=datetime.now(timezone.utc).date(),
        created_by="user1",
        image_url="/images/test1.jpg",
        type="leaf",
        processing_status="completed",
    )

    sample2 = Sample(
        id="sample2",
        record_id="record2",
        created_date=datetime.now(timezone.utc).date(),
        created_by="user1",
        image_url="/images/test2.jpg",
        type="spike",
        processing_status="in_progress",
    )

    # Create mask and bounding box for sample1
    mask1 = Mask(image_id="sample1", mask="base64_encoded_mask_data")
    bbox1 = BoundingBox(image_id="sample1", box="[10, 20, 100, 200]")

    db.session.add_all(
        [user1, group1, record1, record2, ownership1, sample1, sample2, mask1, bbox1]
    )
    db.session.commit()

    return {
        "user1": user1,
        "group1": group1,
        "record1": record1,
        "record2": record2,
        "sample1": sample1,
        "sample2": sample2,
    }


class TestSampleRepository:
    def test_get_by_id(self, database, test_data):
        sample = SampleRepository.get_by_id("sample1")

        # Assert
        assert sample is not None
        assert sample.id == "sample1"
        assert sample.type == "leaf"
        assert sample.processing_status == "completed"

    def test_get_by_record_id(self, database, test_data):
        samples = SampleRepository.get_by_record_id("record1")

        # Assert
        assert len(samples) == 1
        assert samples[0].id == "sample1"

        # Test with another record
        samples2 = SampleRepository.get_by_record_id("record2")
        assert len(samples2) == 1
        assert samples2[0].id == "sample2"

    def test_get_by_owner_id(self, database, test_data):
        group = test_data["group1"]
        samples = SampleRepository.get_by_owner_id(group)

        # Assert
        assert len(samples) == 1
        assert samples[0].id == "sample1"

    def test_create(self, database, test_data):
        sample_id = str(uuid.uuid4())
        new_sample = Sample(
            id=sample_id,
            record_id="record1",
            created_date=datetime.now(timezone.utc).date(),
            created_by="user1",
            image_url="/images/new_test.jpg",
            type="leaf",
            processing_status="pending",
        )

        # Act
        created_sample = SampleRepository.create(new_sample)

        # Assert
        assert created_sample is not None
        assert created_sample.id == sample_id

        # Verify sample was saved to the database
        saved_sample = Sample.query.get(sample_id)
        assert saved_sample is not None
        assert saved_sample.image_url == "/images/new_test.jpg"
        assert saved_sample.processing_status == "pending"

    def test_update(self, database, test_data):
        sample = test_data["sample1"]
        sample.processing_status = "failed"

        updated_sample = SampleRepository.update(sample)

        # Assert
        assert updated_sample is not None
        assert updated_sample.processing_status == "failed"

        # Verify changes were saved to the database
        db.session.expire_all()  # Clear session cache
        saved_sample = Sample.query.get("sample1")
        assert saved_sample.processing_status == "failed"

    def test_delete(self, database, test_data):
        sample = test_data["sample2"]

        SampleRepository.delete(sample)

        # Verify sample was removed from database
        deleted_sample = Sample.query.get("sample2")
        assert deleted_sample is None
