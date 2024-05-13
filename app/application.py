import os
import uuid
from application_interface import ApplicationInterface

class Application(ApplicationInterface):
    def __init__(self, image_folder="images", jobs="jobs"):
        self.image_folder = image_folder
        os.makedirs(self.image_folder, exist_ok=True)

        self._jobs = {}
        os.makedirs(jobs, exist_ok=True)

        self.jobs_file = os.path.join(jobs, "jobs.csv")
        if os.path.exists(self.jobs_file):
            with open(self.jobs_file, 'r') as fs:
                line = fs.readline()
                while line:
                    info = line.replace(" ", "").split(",")
                    self._jobs[info[0]] = {
                        "job_id": info[0],
                        "status": info[1],
                        "image": info[2]
                    }
                    line = fs.readline()
        else:
            with open(self.jobs_file, 'w') as fs:
                pass

    def submit_job(self, file):
        guid = str(uuid.uuid4())
        # TODO: Check if the image is valid
        with open(os.path.join(self.image_folder, f'{guid}.jpeg'), 'wb') as fs:
            fs.write(file)

        self._jobs[guid] = {
            "job_id": guid,
            "status": "submitted",
            "image": f"{guid}.jpeg"
        }
        self.record_job(guid)

        return guid
    
    def record_job(self, job_id):
        with open(self.jobs_file, 'a') as fs:
            fs.write(f"{job_id},submitted,{job_id}.jpeg\n")
    
    def job_status(self, job_id):
        if job_id in self._jobs:
            return self._jobs[job_id]["status"]
        return "job not found"
    
    def job_data(self, job_id):
        response = {"id": "", "status": "", "image": ""}
        if job_id in self._jobs:
            job = self._jobs[job_id]
            response["id"] = job_id
            response["status"] = job["status"]
            response["image"] = job["image"]

        return response
    
    def get_image(self, job_id, image_name):
        image_file_path = os.path.join(self.image_folder, self._jobs[job_id][image_name])
        
        if os.path.exists(image_file_path):
            return open(image_file_path, 'rb')
        else:
            return None
        
