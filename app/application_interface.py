from abc import ABC, abstractmethod

class ApplicationInterface(ABC):
    @abstractmethod
    def submit_job(self, image):
        pass

    @abstractmethod
    def job_status(self, job_id):
        pass

    @abstractmethod
    def job_data(self, job_id):
        pass

    @abstractmethod
    def get_image(self ,job_id, image_name):
        pass