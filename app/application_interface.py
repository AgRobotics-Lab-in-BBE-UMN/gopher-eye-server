from abc import ABC, abstractmethod

class ApplicationInterface(ABC):
    @abstractmethod
    def segment_plant(self, image):
        pass

    @abstractmethod
    def plant_status(self, plant_id):
        pass

    @abstractmethod
    def plant_data(self, plant_id):
        pass

    @abstractmethod
    def get_image(self ,plant_id, image_name):
        pass