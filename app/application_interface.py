from abc import ABC, abstractmethod

class ApplicationInterface(ABC):
    # @abstractmethod
    # def segment_plant(self, image):
    #     pass

    # @abstractmethod
    # def plant_status(self, plant_id):
    #     pass

    # @abstractmethod
    # def plant_data(self, plant_id):
    #     pass

    # @abstractmethod
    # def get_image(self ,plant_id, image_name):
    #     pass

    # @abstractmethod
    # def get_plant_ids(self):
    #     pass
    
    @abstractmethod
    def register_user(self, session, user):
        pass
    
    @abstractmethod
    def get_records_id(self, user_id):
        pass
    
    @abstractmethod
    def get_record(self, record_id):
        pass
    
    @abstractmethod
    def get_samples(self, record_id):
        pass
    
    @abstractmethod
    def get_sample(self, sample_id):
        pass
    
    @abstractmethod
    def get_sample_image(self, sample_id, image_name):
        pass
    
    @abstractmethod
    def get_masks(self, sample_id):
        pass
    
    @abstractmethod
    def get_boxes(self, mask_id):
        pass
    
    @abstractmethod
    def create_record(self, session, record, user):
        pass
    
    @abstractmethod
    def create_sample(self, session, sample, record):
        pass
    
    @abstractmethod
    def segment_sample(self, sample_id):
        pass