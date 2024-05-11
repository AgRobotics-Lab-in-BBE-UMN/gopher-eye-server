import pytest
from api import create_app, ApplicationLayer
import os


application_layer = ApplicationLayer()

@pytest.fixture()
def server():
    app = create_app("test", application_layer=application_layer)
    app.config.update({"TESTING": True, "DEBUG": True})
    
    yield app


@pytest.fixture()
def client(server):
    return server.test_client()


def test_job_submission(client):
    # Given
    image = open('0025.jpg', 'rb')
    data = {'image': image}
    header = {'content-type': 'multipart/form-data'}
    
    # When
    response = client.put("/dl/segmentation", headers=header, data=data)
    
    # Then
    guid = response.text
    assert os.path.exists(f"images/{guid}.jpeg")

def test_job_status_valid(client):
    # Given
    job_id = 'test_guid'
    header = {'content-type': 'application/json'}
    json = {'job_id': job_id}

    application_layer.record_job(job_id)
    
    # When
    response = client.get("/job/status", headers=header, json=json)
    
    # Then
    assert response.text == "submitted"

def test_job_statu_bad(client):
    # Given
    header = {'content-type': 'application/json'}
    json = {'job_id': 'not real id'}
    
    # When
    response = client.get("/job/status", headers=header, json=json)
    
    # Then
    assert response.text == "job not found"