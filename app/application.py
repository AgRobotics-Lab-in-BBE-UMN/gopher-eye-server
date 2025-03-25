import os
import uuid
from ultralytics import YOLO
from app.application_interface import ApplicationInterface
from app.classification import Classification
import json
from PIL import Image
import numpy as np
import cv2
from scipy import ndimage

LEAF_MODEL = "models/leaf-yolo11m-seg.pt"
SPIKE_MODEL = "models/spike-yolo11x-seg.pt"

class Application(ApplicationInterface):
    def __init__(self, image_folder="images", plants="plants"):
        self.image_folder = image_folder
        os.makedirs(self.image_folder, exist_ok=True)

        self._plants = {}
        os.makedirs(plants, exist_ok=True)

        self.plants_file = os.path.join(plants, "plants.json")
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

        self.segmentation = YOLO(LEAF_MODEL)
        self.segmentation_spike = YOLO(SPIKE_MODEL)
        label2id = {'Healthy-Leaf': 0, 'Downy-Leaf': 1, 'Powdery-Leaf': 2}
        id2label = {0: 'Healthy-Leaf', 1: 'Downy-Leaf', 2: 'Powdery-Leaf'}
        self.classification = Classification("models/swinv2-tiny-patch4-window8-256", label2id=label2id, id2label=id2label)

    def segment_plant(self, file, task='leaf'):
        guid = str(uuid.uuid4())
        # TODO: Check if the image is valid

        try:
            with open(os.path.join(self.image_folder, f'{guid}.jpeg'), 'wb') as fs:
                fs.write(file)
        except:
            return None

        if task == 'leaf':
            results = self.segmentation(os.path.join(self.image_folder, f'{guid}.jpeg'))[0]
        elif task == 'spike':
            results = self.segmentation_spike(os.path.join(self.image_folder, f'{guid}.jpeg'))[0]

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
        
        for i, mask_points in enumerate(self._plants[guid]["masks"]):
            image = self.read_image(os.path.join(self.image_folder, f'{guid}.jpeg'))
            
            mask = self._points_to_mask(mask_points, image.shape)
            subimage = self._crop_image(image, mask)
            cropped_mask = self._crop_image(mask, mask)
            
            if task == 'leaf':
                label = self.classification.classify(cropped_mask * subimage)
            elif task == 'spike':
                label = self._score_spike(subimage, cropped_mask)
            else:
                label = "Unknown"
                
            self._plants[guid]["labels"].append(label)
            
        self.record_plant(self._plants[guid])

        return guid
    
    def read_image(self, path):
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img
    
    def _score_spike(self, image, mask, alpha=0.81):
        masked_image = image * mask
        
        b = masked_image[:,:,0]
        g = masked_image[:,:,1]

        bg = alpha * b - g
        bg[bg < 0] = 0
        bg[bg > 0] = 1
        
        labeled_array, num_features = ndimage.label(bg)
        min_area = 0.0005 * masked_image.shape[0] * masked_image.shape[1]
        
        filtered_bg = np.zeros_like(bg)
        
        large_regions = 0
        
        for label in range(1, num_features+1):
            region = labeled_array == label
            if np.sum(region) > min_area:
                filtered_bg[region] = 1
                large_regions += 1
                

        return f'FHB: {np.sum(filtered_bg) / np.sum(mask):.2f}'
    
    def _points_to_mask(self, points, img_shape):
        mask = np.zeros(img_shape[:-1], dtype=np.uint8)
        points = points * np.flip(img_shape[:-1])
        points = points.reshape(-1, 1, 2).astype(int)
        
        cv2.fillPoly(mask, [points], 1)
        return mask[:,:, np.newaxis]
    
    def _get_mask_bounding_box(self, mask):
        mask = mask.squeeze()
        y, x = np.where(mask)
        return np.min(x), np.min(y), np.max(x), np.max(y)
    
    def _crop_image(self, image, mask):
        x1, y1, x2, y2 = self._get_mask_bounding_box(mask)
        return image[y1:y2, x1:x2]
    
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