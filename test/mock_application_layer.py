from app.application_interface import ApplicationInterface


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
    
    def get_plant_ids(self):
        return list(self.plants.keys())
