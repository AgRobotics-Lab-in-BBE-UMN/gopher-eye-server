import os
import uuid
from application_interface import ApplicationInterface
from ultralytics import YOLO
from classification import Classification
import json
from PIL import Image
import numpy as np

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
                    data = json.loads(line)
                    self._plants[data["plant_id"]] = {
                        "plant_id": data["plant_id"],
                        "status": data["status"],
                        "image": data["image"],
                        "bounding_boxes": data["bounding_boxes"],
                        "masks": data["masks"],
                        "labels": data["labels"]
                    }
                    line = fs.readline()
        else:
            with open(self.plants_file, 'w') as fs:
                pass

        self.segmentation = YOLO("yolo11s-seg.pt")
        label2id = {'Healthy-Leaf': 0, 'Downy-Leaf': 1, 'Powdery-Leaf': 2}
        id2label = {0: 'Healthy-Leaf', 1: 'Downy-Leaf', 2: 'Powdery-Leaf'}
        self.classification = Classification("swinv2-tiny-patch4-window8-256", label2id=label2id, id2label=id2label)

    def segment_plant(self, file):
        guid = str(uuid.uuid4())
        # TODO: Check if the image is valid

        try:
            with open(os.path.join(self.image_folder, f'{guid}.jpeg'), 'wb') as fs:
                fs.write(file)
        except:
            return None

        results = self.segmentation(os.path.join(self.image_folder, f'{guid}.jpeg'))[0]
        self._plants[guid] = {
            "plant_id": guid,
            "status": "complete",
            "image": f"{guid}.jpeg",
            "bounding_boxes": [],
            "masks": [],
            "labels": []
        }

        if results.boxes:
            self._plants[guid]["bounding_boxes"] = results.boxes.xyxyn.tolist()

        if results.masks:
            self._plants[guid]["masks"] = [mask.tolist() for mask in results.masks.xyn]
        
        for i, mask in enumerate(self._plants[guid]["masks"]):
            image = Image.open(os.path.join(self.image_folder, f'{guid}.jpeg'))
            bbox = self._plants[guid]["bounding_boxes"][i]
            left = int(bbox[0] * image.width)
            top = int(bbox[1] * image.height)
            right = int(bbox[2] * image.width)
            bottom = int(bbox[3] * image.height)
            subimage = image.crop((left, top, right, bottom))
            label = self.classification.classify(subimage)
            self._plants[guid]["labels"].append(label)
            
        self.record_plant(self._plants[guid])

        return guid
    
    def record_plant(self, data):
        with open(self.plants_file, 'a') as fs:
            fs.write(f"{json.dumps(data)}\n")
    
    def plant_status(self, plant_id):
        if plant_id in self._plants:
            return self._plants[plant_id]["status"]
        return "plant not found"
    
    def plant_data(self, plant_id):
        response = {}
        if plant_id in self._plants:
            response = self._plants[plant_id]

        return response
    
    def get_image(self, plant_id, image_name):
        # TODO: This needs a custom error message
        try:
            image_file_path = os.path.join(self.image_folder, self._plants[plant_id][image_name].rstrip())
            return open(image_file_path, 'rb'), "image/png" if ("png" in image_file_path) else "image/jpeg"
        except:
            return None, None
        
    def get_plant_ids(self):
        return list(self._plants.keys())