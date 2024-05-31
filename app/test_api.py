import pytest
from api import create_api
from application_interface import ApplicationInterface
import os
import uuid

class MockApplicationLayer(ApplicationInterface):
    def __init__(self):
        self.plants = {}
        self.image_folder = "images"
        self.response_guid = None

    def set_reponse_guid(self, guid):
        self.response_guid = guid

    def segment_plant(self, _):
        guid = self.response_guid if self.response_guid else str(uuid.uuid4())
        self.plants[guid] = {
            "plant_id": guid,
            "status": "submitted",
            "image": f"{guid}.jpeg",
            "masks": [[[0, 0], [1, 1]]],
            "bounding_boxes": [[0.25, 0.25, 0.5, 0.5]]
        }
        return guid
    
    def create_plant(self, plant_id, status="submitted", image=None):
        self.plants[plant_id] = {
            "plant_id": plant_id,
            "status": status,
            "image": f"{plant_id}.jpeg" if image is None else image,
            "masks": [[[0, 0], [1, 1]]],
            "bounding_boxes": [[0.25, 0.25, 0.5, 0.5]]
        }

    def set_plant_status(self, plant_id, status):
        self.plants[plant_id]["status"] = status

    def clear_plants(self):
        self.plants = {}

    def plant_status(self, plant_id):
        if plant_id in self.plants:
            return self.plants[plant_id]["status"]
        return "plant_not_found"
    
    def plant_data(self, plant_id):
        response = {"plant_id": "", "status": "", "image": "", "masks": [], "bounding_boxes": []}
        if plant_id in self.plants:
            response = self.plants[plant_id]

        return response
    
    def get_image(self, plant_id, image_name):
        plants = {"test_guid": {"image": "0025.jpg", "segmentation": "0025_segmentation.png"}}
        try:
            file = plants[plant_id][image_name]
            fs = open(file, 'rb')
            return fs, "image/png" if ("png" in file) else "image/jpeg"
        except:
            return None, None
        
    def set_plant_ids(self, ids):
        for id in ids:
            self.create_plant(id)
    
    def get_plant_ids(self):
        return list(self.plants.keys())

mock_application_layer = MockApplicationLayer()

@pytest.fixture()
def server():
    app = create_api("test", application_layer=mock_application_layer)
    app.config.update({"TESTING": True, "DEBUG": True})
    
    yield app

@pytest.fixture()
def client(server):
    return server.test_client()

def test_plant_submission_valid(client):
    # Given
    image = open('0025.jpg', 'rb')
    data = {'image': image}
    header = {'content-type': 'multipart/form-data'}
    guid = str(uuid.uuid4())
    mock_application_layer.clear_plants()
    mock_application_layer.set_reponse_guid(guid)

    # When
    response = client.put("/dl/segmentation", headers=header, data=data)
    
    # Then
    assert guid == response.json["plant_id"]

def test_plant_submission_bad_message_type(client):
    # Given
    data = {'image': 'not an image'}
    header = {'content-type': 'application/json'}
    
    # When
    response = client.put("/dl/segmentation", headers=header, data=data)
    
    # Then
    assert response.status_code == 400

def test_plant_submission_no_image(client):
    # Given
    data = {'not_image': 'not an image'}
    header = {'content-type': 'multipart/form-data'}
    
    # When
    response = client.put("/dl/segmentation", headers=header, data=data)
    
    # Then
    assert response.status_code == 400

def test_plant_status_valid(client):
    # Given
    plant_id = 'test_guid'
    query_string = {'plant_id': plant_id}

    mock_application_layer.clear_plants()
    mock_application_layer.create_plant(plant_id, status="test_status")
    
    # When
    response = client.get("/plant/status", query_string=query_string)
    
    # Then
    assert response.json["status"] == "test_status"

def test_plant_status_bad(client):
    # Given
    json = {'plant_id': 'not real id'}
    
    # When
    response = client.get("/plant/status", json=json)
    
    # Then
    assert response.json["status"] == "plant_not_found"

def test_plant_data_valid(client):
    # Given
    plant_id = 'test_guid'
    query_string = {'plant_id': plant_id}

    mock_application_layer.clear_plants()
    mock_application_layer.create_plant(plant_id, status="complete")
    
    # When
    response = client.get("/plant/data", query_string=query_string)
    
    # Then
    assert response.json == {"plant_id": plant_id, "status": "complete", "image": f"{plant_id}.jpeg", "masks": [[[0, 0], [1, 1]]], "bounding_boxes": [[0.25, 0.25, 0.5, 0.5]]}

def test_plant_data_bad(client):
    # Given
    query_string = {'plant_id': 'not real id'}

    mock_application_layer.clear_plants()
    mock_application_layer.create_plant('test_guid', status="complete")
    
    # When
    response = client.get("/plant/data", query_string=query_string)
    
    # Then
    assert response.json == {"plant_id": "", "status": "", "image": "", "masks": [], "bounding_boxes": []}

def test_plant_get_image_valid_image(client):
    # Given
    plant_id = 'test_guid'
    query_string = {'plant_id': plant_id, 'image_name': 'image'}
    
    # When
    response = client.get("/plant/image", query_string=query_string)
    
    # Then
    assert response.status_code == 200
    assert response.mimetype == 'image/jpeg'
    assert response.data == open('0025.jpg', 'rb').read()

def test_plant_get_image_valid_segmentation(client):
    # Given
    plant_id = 'test_guid'
    query_string = {'plant_id': plant_id, 'image_name': 'segmentation'}
    
    # When
    response = client.get("/plant/image", query_string=query_string)
    
    # Then
    assert response.status_code == 200
    assert response.mimetype == 'image/png'
    assert response.data == open('0025_segmentation.png', 'rb').read()

def test_plant_handles_bad_image_name_grab(client):
    # Given
    plant_id = 'test_guid'
    query_string = {'plant_id': plant_id, 'image_name': 'image_not_found'}
    
    # When
    response = client.get("/plant/image", query_string=query_string)
    
    # Then
    assert response.status_code == 400

def test_plant_handles_bad_guid(client):
    # Given
    plant_id = 'bad_test_guid'
    query_string = {'plant_id': plant_id, 'image_name': 'image_not_found'}
    
    # When
    response = client.get("/plant/image", query_string=query_string)
    
    # Then
    assert response.status_code == 400

def test_get_plant_ids(client):
    # Given
    plant_ids = ['1', '2', '3', '4', '5']
    mock_application_layer.set_plant_ids(plant_ids)
    
    # When
    response = client.get("/plant/ids")
    
    # Then
    assert response.status_code == 200
    assert response.json == {"plant_ids": plant_ids}

def test_get_plant_id_no_ids(client):
    # Given
    plant_ids = []
    mock_application_layer.set_plant_ids(plant_ids)
    
    # When
    response = client.get("/plant/ids")
    
    # Then
    assert response.status_code == 200
    assert response.json == {"plant_ids": plant_ids}
