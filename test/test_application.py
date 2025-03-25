import pytest
import ultralytics.engine
from app.application import Application
from shutil import rmtree
import os


@pytest.fixture
def cleanup():
    to_delete = []
    yield to_delete
    for item in to_delete:
        if os.path.exists(item):
            rmtree(item)


def test_app_init(cleanup):
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    cleanup += [test_image_dir, test_plants_dir]

    # When
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)

    # Then
    assert app.image_folder == test_image_dir
    assert app.plants_file == f"{test_plants_dir}/plants.json"
    assert os.path.exists(test_image_dir)
    assert os.path.exists(test_plants_dir)
    assert os.path.exists(test_image_dir)
    assert os.path.exists(app.plants_file)


def test_submit_plant(cleanup):
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    image_data = open("0025.jpg", "rb").read()
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)
    cleanup += [test_image_dir, test_plants_dir]

    # When
    guid = app.segment_plant(image_data)

    # Then
    assert os.path.exists(os.path.join(test_image_dir, f"{guid}.jpeg"))
    assert app._plants[guid]["status"] == "complete"
    assert app._plants[guid]["image"] == f"{guid}.jpeg"
    assert open(os.path.join(test_image_dir, f"{guid}.jpeg"), "rb").read() == image_data


def test_plant_status(cleanup):
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    image_data = open("0025.jpg", "rb").read()
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)
    guid = app.segment_plant(image_data)
    cleanup += [test_image_dir, test_plants_dir]

    # When
    status = app.plant_status(guid)

    # Then
    assert status == "complete"


def test_plant_data(cleanup):
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    image_data = open("0025.jpg", "rb").read()
    cleanup += [test_image_dir, test_plants_dir]
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)
    guid = app.segment_plant(image_data)

    # When
    data = app.plant_data(guid)

    # Then
    assert data["plant_id"] == guid
    assert data["status"] == "complete"
    assert data["image"] == f"{guid}.jpeg"
    assert data["masks"] == app._plants[guid]["masks"]
    assert data["bounding_boxes"] == app._plants[guid]["bounding_boxes"]


def test_plant_data_invalid_plant_id(cleanup):
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    cleanup += [test_image_dir, test_plants_dir]
    image_data = open("0025.jpg", "rb").read()
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)
    guid = app.segment_plant(image_data)

    # When
    data = app.plant_data("invalid-plant-id")

    # Then
    assert data.items() == {}.items()


def test_get_image(cleanup):
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    cleanup += [test_image_dir, test_plants_dir]
    image_data = open("0025.jpg", "rb").read()
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)
    guid = app.segment_plant(image_data)

    # When
    image, mimetype = app.get_image(guid, "image")

    # Then
    assert image.read() == image_data
    assert mimetype == "image/jpeg"


def test_get_image_invalid_image_entry(cleanup):
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    cleanup += [test_image_dir, test_plants_dir]
    image_data = open("bad.jpeg", "rb").read()
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)
    guid = app.segment_plant(image_data)

    # When
    image, mimetype = app.get_image(guid, "invalid-image")

    # Then
    assert image == None
    assert mimetype == None


def test_segment_plant_valid_image(cleanup):
    import ultralytics

    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    cleanup += [test_image_dir, test_plants_dir]
    image_data = open("0025.jpg", "rb").read()
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)

    # When
    guid = app.segment_plant(image_data)

    # Then
    data = app.plant_data(guid)
    assert guid != None
    assert data["plant_id"] == guid
    assert data["status"] == "complete"
    assert data["image"] == f"{guid}.jpeg"
    assert isinstance(data["masks"], list)
    assert isinstance(data["masks"][0], list)
    assert isinstance(data["masks"][0][0], list)
    assert len(data["masks"]) > 0
    assert len(data["masks"][0]) > 0
    assert len(data["masks"][0][0]) == 2


def test_segment_plant_invalid_image(cleanup):
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    cleanup += [test_image_dir, test_plants_dir]
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)

    # When
    guid = app.segment_plant(None)

    # Then
    assert guid == None


def test_get_plant_ids(cleanup):
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    cleanup += [test_image_dir, test_plants_dir]
    image_data = open("0025.jpg", "rb").read()
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)
    guids = [app.segment_plant(image_data) for i in range(5)]

    # When
    plant_ids = app.get_plant_ids()

    # Then
    assert plant_ids == guids


def test_get_plant_ids_empty(cleanup):
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    cleanup += [test_image_dir, test_plants_dir]
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)

    # When
    plant_ids = app.get_plant_ids()

    # Then
    assert plant_ids == []
