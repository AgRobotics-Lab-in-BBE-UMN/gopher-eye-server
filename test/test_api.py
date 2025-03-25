import pytest
from app.router import create_api
import uuid

from test.mock_application_layer import MockApplicationLayer

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
    mock_application_layer.clear_plants()
    for plant_id in plant_ids:
        mock_application_layer.create_plant(plant_id)
    
    # When
    response = client.get("/plant/ids")
    
    # Then
    assert response.status_code == 200
    assert response.json == {"plant_ids": plant_ids}

def test_get_plant_id_no_ids(client):
    # Given
    plant_ids = []
    mock_application_layer.clear_plants()
    mock_application_layer.clear_plants()
    for plant_id in plant_ids:
        mock_application_layer.create_plant(plant_id)
    
    # When
    response = client.get("/plant/ids")
    
    # Then
    assert response.status_code == 200
    assert response.json == {"plant_ids": plant_ids}
