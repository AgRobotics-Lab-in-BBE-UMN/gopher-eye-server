import os
import shutil
import uuid
from application_interface import ApplicationInterface

class Application(ApplicationInterface):
    def __init__(self, image_folder="images", plants="plants"):
        self.image_folder = image_folder
        os.makedirs(self.image_folder, exist_ok=True)

        self._plants = {}
        os.makedirs(plants, exist_ok=True)

        self.plants_file = os.path.join(plants, "plants.csv")
        if os.path.exists(self.plants_file):
            with open(self.plants_file, 'r') as fs:
                line = fs.readline()
                while line:
                    info = line.replace(" ", "").split(",")
                    self._plants[info[0]] = {
                        "plant_id": info[0],
                        "status": info[1],
                        "image": info[2],
                        "segmentation": info[3]
                    }
                    line = fs.readline()
        else:
            with open(self.plants_file, 'w') as fs:
                pass

    def segment_plant(self, file):
        guid = str(uuid.uuid4())
        # TODO: Check if the image is valid
        with open(os.path.join(self.image_folder, f'{guid}.jpeg'), 'wb') as fs:
            fs.write(file)

        # TODO: Replacce with segementation model call
        shutil.copyfile('0025_segmentation.png', os.path.join(self.image_folder, f'{guid}_segmentation.png'))
        self._plants[guid] = {
            "plant_id": guid,
            "status": "complete",
            "image": f"{guid}.jpeg",
            "segmentation": f"{guid}_segmentation.png"
        }
        self.record_plant(guid, self._plants[guid]["status"])

        return guid
    
    def record_plant(self, plant_id, status):
        with open(self.plants_file, 'a') as fs:
            fs.write(f"{plant_id},status,{plant_id}.jpeg,{plant_id}.png\n")
    
    def plant_status(self, plant_id):
        if plant_id in self._plants:
            return self._plants[plant_id]["status"]
        return "plant not found"
    
    def plant_data(self, plant_id):
        response = {"id": "", "status": "", "image": ""}
        if plant_id in self._plants:
            plant = self._plants[plant_id]
            response["id"] = plant_id
            response["status"] = plant["status"]
            response["image"] = plant["image"]
            response["segmentation"] = plant["segmentation"]

        return response
    
    def get_image(self, plant_id, image_name):
        # TODO: This needs a custom error message
        try:
            image_file_path = os.path.join(self.image_folder, self._plants[plant_id][image_name])
            return open(image_file_path, 'rb'), "image/png" if ("png" in image_file_path) else "image/jpeg"
        except:
            return None, None
        
