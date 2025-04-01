from abc import ABC, abstractmethod

class ApplicationInterface(ABC):
    @abstractmethod
    def register_user(self, session, user):
        pass
    
    @abstractmethod
    def get_user_records(self, session, user_id):
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
    
    @abstractmethod
    def get_samples(self, session, user_id, record_id):
        pass