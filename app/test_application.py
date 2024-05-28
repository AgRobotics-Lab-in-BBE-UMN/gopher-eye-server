import pytest
from application import Application
from shutil import rmtree
import os

def test_app_init():
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"

    # When
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)

    # Then
    assert app.image_folder == test_image_dir
    assert app.plants_file == f"{test_plants_dir}/plants.csv"
    assert os.path.exists(test_image_dir)
    assert os.path.exists(test_plants_dir)
    assert os.path.exists(test_image_dir)
    assert os.path.exists(app.plants_file)

    # Clean up
    rmtree(test_image_dir)
    rmtree(test_plants_dir)

def test_submit_plant():
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    image_data = open("0025.jpg", "rb").read()
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)

    # When
    guid = app.segment_plant(image_data)

    # Then
    assert os.path.exists(os.path.join(test_image_dir, f"{guid}.jpeg"))
    assert app._plants[guid]["status"] == "complete"
    assert app._plants[guid]["image"] == f"{guid}.jpeg"
    assert open(os.path.join(test_image_dir, f"{guid}.jpeg"), "rb").read() == image_data

    # Clean up
    rmtree(test_image_dir)
    rmtree(test_plants_dir)

def test_plant_status():
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    image_data = open("0025.jpg", "rb").read()
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)
    guid = app.segment_plant(image_data)

    # When
    status = app.plant_status(guid)

    # Then
    assert status == "complete"

    # Clean up
    rmtree(test_image_dir)
    rmtree(test_plants_dir)

def test_plant_data():
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    image_data = open("0025.jpg", "rb").read()
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)
    guid = app.segment_plant(image_data)

    # When
    data = app.plant_data(guid)

    # Then
    assert data["id"] == guid
    assert data["status"] == "complete"
    assert data["image"] == f"{guid}.jpeg"
    assert data["segmentation"] == f"{guid}_segmentation.jpeg"

    # Clean up
    rmtree(test_image_dir)
    rmtree(test_plants_dir)

def test_plant_data_invalid_plant_id():
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    image_data = open("0025.jpg", "rb").read()
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)
    guid = app.segment_plant(image_data)

    # When
    data = app.plant_data("invalid-plant-id")

    # Then
    assert data["id"] == ""
    assert data["status"] == ""
    assert data["image"] == ""

    # Clean up
    rmtree(test_image_dir)
    rmtree(test_plants_dir)

def test_get_image():
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    image_data = open("0025.jpg", "rb").read()
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)
    guid = app.segment_plant(image_data)

    # When
    image, mimetype = app.get_image(guid, "image")

    # Then
    assert image.read() == image_data
    assert mimetype == "image/jpeg"

    # Clean up
    rmtree(test_image_dir)
    rmtree(test_plants_dir)

def test_get_image_invalid_image_entry():
    # Given
    test_image_dir = "test-images"
    test_plants_dir = "test-plants"
    image_data = open("0025_segmentation.png", "rb").read()
    app = Application(image_folder=test_image_dir, plants=test_plants_dir)
    guid = app.segment_plant(image_data)

    # When
    image, mimetype = app.get_image(guid, "invalid-image")

    # Then
    assert image == None
    assert mimetype == None

    # Clean up
    rmtree(test_image_dir)
    rmtree(test_plants_dir)