import pytest
from application import Application
from shutil import rmtree
import os

def test_app_init():
    # Given
    test_image_dir = "test-images"
    test_jobs_dir = "test-jobs"

    # When
    app = Application(image_folder=test_image_dir, jobs=test_jobs_dir)

    # Then
    assert app.image_folder == test_image_dir
    assert app.jobs_file == f"{test_jobs_dir}/jobs.csv"
    assert os.path.exists(test_image_dir)
    assert os.path.exists(test_jobs_dir)
    assert os.path.exists(test_image_dir)
    assert os.path.exists(app.jobs_file)

    # Clean up
    rmtree(test_image_dir)
    rmtree(test_jobs_dir)

def test_submit_job():
    # Given
    test_image_dir = "test-images"
    test_jobs_dir = "test-jobs"
    image_data = open("0025.jpg", "rb").read()
    app = Application(image_folder=test_image_dir, jobs=test_jobs_dir)

    # When
    guid = app.submit_job(image_data)

    # Then
    assert os.path.exists(os.path.join(test_image_dir, f"{guid}.jpeg"))
    assert app._jobs[guid]["status"] == "submitted"
    assert app._jobs[guid]["image"] == f"{guid}.jpeg"
    assert open(os.path.join(test_image_dir, f"{guid}.jpeg"), "rb").read() == image_data

    # Clean up
    rmtree(test_image_dir)
    rmtree(test_jobs_dir)

def test_job_status():
    # Given
    test_image_dir = "test-images"
    test_jobs_dir = "test-jobs"
    image_data = open("0025.jpg", "rb").read()
    app = Application(image_folder=test_image_dir, jobs=test_jobs_dir)
    guid = app.submit_job(image_data)

    # When
    status = app.job_status(guid)

    # Then
    assert status == "submitted"

    # Clean up
    rmtree(test_image_dir)
    rmtree(test_jobs_dir)

def test_job_data():
    # Given
    test_image_dir = "test-images"
    test_jobs_dir = "test-jobs"
    image_data = open("0025.jpg", "rb").read()
    app = Application(image_folder=test_image_dir, jobs=test_jobs_dir)
    guid = app.submit_job(image_data)

    # When
    data = app.job_data(guid)

    # Then
    assert data["id"] == guid
    assert data["status"] == "submitted"
    assert data["image"] == f"{guid}.jpeg"

    # Clean up
    rmtree(test_image_dir)
    rmtree(test_jobs_dir)

def test_job_data_invalid_job_id():
    # Given
    test_image_dir = "test-images"
    test_jobs_dir = "test-jobs"
    image_data = open("0025.jpg", "rb").read()
    app = Application(image_folder=test_image_dir, jobs=test_jobs_dir)
    guid = app.submit_job(image_data)

    # When
    data = app.job_data("invalid-job-id")

    # Then
    assert data["id"] == ""
    assert data["status"] == ""
    assert data["image"] == ""

    # Clean up
    rmtree(test_image_dir)
    rmtree(test_jobs_dir)

def test_get_image():
    # Given
    test_image_dir = "test-images"
    test_jobs_dir = "test-jobs"
    image_data = open("0025.jpg", "rb").read()
    app = Application(image_folder=test_image_dir, jobs=test_jobs_dir)
    guid = app.submit_job(image_data)

    # When
    image = app.get_image(guid, "image")

    # Then
    assert image.read() == image_data

    # Clean up
    rmtree(test_image_dir)
    rmtree(test_jobs_dir)