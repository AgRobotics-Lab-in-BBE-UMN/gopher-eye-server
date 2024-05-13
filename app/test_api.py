import pytest
from api import create_api
from application_interface import ApplicationInterface
import os
import uuid

class MockApplicationLayer(ApplicationInterface):
    def __init__(self):
        self.jobs = {}
        self.image_folder = "images"
        self.response_guid = None

    def set_reponse_guid(self, guid):
        self.response_guid = guid

    def submit_job(self, _):
        guid = self.response_guid if self.response_guid else str(uuid.uuid4())
        self.jobs[guid] = {
            "job_id": guid,
            "status": "submitted",
            "image": f"{guid}.jpeg"
        }
        return guid
    
    def create_job(self, job_id, status="submitted", image=None):
        self.jobs[job_id] = {
            "job_id": job_id,
            "status": status,
            "image": f"{job_id}.jpeg" if image is None else image
        }

    def set_job_status(self, job_id, status):
        self.jobs[job_id]["status"] = status

    def clear_jobs(self):
        self.jobs = {}

    def job_status(self, job_id):
        if job_id in self.jobs:
            return self.jobs[job_id]["status"]
        return "job_not_found"
    
    def job_data(self, job_id):
        response = {"id": "", "status": "", "image": ""}
        if job_id in self.jobs:
            job = self.jobs[job_id]
            response["id"] = job_id
            response["status"] = job["status"]
            response["image"] = job["image"]

        return response
    
    def get_image(self, job_id, image_name):
        try :
            fs = open(image_name, 'rb')
            return fs
        except:
            return None

mock_application_layer = MockApplicationLayer()

@pytest.fixture()
def server():
    app = create_api("test", application_layer=mock_application_layer)
    app.config.update({"TESTING": True, "DEBUG": True})
    
    yield app

@pytest.fixture()
def client(server):
    return server.test_client()

def test_job_submission_valid(client):
    # Given
    image = open('0025.jpg', 'rb')
    data = {'image': image}
    header = {'content-type': 'multipart/form-data'}
    guid = str(uuid.uuid4())
    mock_application_layer.clear_jobs()
    mock_application_layer.set_reponse_guid(guid)

    # When
    response = client.put("/dl/segmentation", headers=header, data=data)
    
    # Then
    assert guid == response.json["job_id"]

def test_job_submission_bad_message_type(client):
    # Given
    data = {'image': 'not an image'}
    header = {'content-type': 'application/json'}
    
    # When
    response = client.put("/dl/segmentation", headers=header, data=data)
    
    # Then
    assert response.status_code == 400

def test_job_submission_no_image(client):
    # Given
    data = {'not_image': 'not an image'}
    header = {'content-type': 'multipart/form-data'}
    
    # When
    response = client.put("/dl/segmentation", headers=header, data=data)
    
    # Then
    assert response.status_code == 400

def test_job_status_valid(client):
    # Given
    job_id = 'test_guid'
    header = {'content-type': 'application/json'}
    json = {'job_id': job_id}

    mock_application_layer.clear_jobs()
    mock_application_layer.create_job(job_id, status="test_status")
    
    # When
    response = client.get("/job/status", headers=header, json=json)
    
    # Then
    assert response.json["status"] == "test_status"

def test_job_statu_bad(client):
    # Given
    header = {'content-type': 'application/json'}
    json = {'job_id': 'not real id'}
    
    # When
    response = client.get("/job/status", headers=header, json=json)
    
    # Then
    assert response.json["status"] == "job_not_found"

def test_job_data_valid(client):
    # Given
    job_id = 'test_guid'
    header = {'content-type': 'application/json'}
    json = {'job_id': job_id}

    mock_application_layer.clear_jobs()
    mock_application_layer.create_job(job_id, status="complete")
    
    # When
    response = client.get("/job/data", headers=header, json=json)
    
    # Then
    assert response.json == {"id": job_id, "status": "complete", "image": f"{job_id}.jpeg"}

def test_job_data_bad(client):
    # Given
    header = {'content-type': 'application/json'}
    json = {'job_id': 'not real id'}

    mock_application_layer.clear_jobs()
    mock_application_layer.create_job('test_guid', status="complete")
    
    # When
    response = client.get("/job/data", headers=header, json=json)
    
    # Then
    assert response.json == {"id": "", "status": "", "image": ""}

def test_job_get_image_valid(client):
    # Given
    job_id = 'test_guid'
    header = {'content-type': 'application/json'}
    json = {'job_id': job_id, 'image': '0025.jpg'}
    
    # When
    response = client.get("/job/image", headers=header, json=json)
    
    # Then
    assert response.status_code == 200
    assert response.mimetype == 'image/jpeg'
    assert response.data == open('0025.jpg', 'rb').read()

def test_job_image_bad(client):
    # Given
    job_id = 'test_guid'
    header = {'content-type': 'application/json'}
    json = {'job_id': job_id, 'image': 'does_not_exist.jpg'}
    
    # When
    response = client.get("/job/image", headers=header, json=json)
    
    # Then
    assert response.status_code == 400
