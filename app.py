import os
import uuid

class ApplicationLayer():
    def __init__(self):
        self.image_folder = "images"
        os.makedirs(self.image_folder, exist_ok=True)

        self.jobs = {}
        os.makedirs("jobs", exist_ok=True)
        if os.path.exists("jobs/jobs.csv"):
            with open("jobs/jobs.csv", 'r') as fs:
                line = fs.readline()
                while line:
                    info = line.replace(" ", "").split(",")
                    self.jobs[info[0]] = {
                        "job_id": info[0],
                        "status": info[1],
                        "image": info[2]
                    }
                    line = fs.readline()

    def submit_job(self, file):
        guid = str(uuid.uuid4())
        # TODO: Check if the image is valid
        with open(f'images/{guid}.jpeg', 'wb') as fs:
            fs.write(file)

        self.jobs[guid] = {
            "job_id": guid,
            "status": "submitted",
            "image": f"{guid}.jpeg"
        }
        self.record_job(guid)

        return guid
    
    def record_job(self, job_id):
        with open("jobs/jobs.csv", 'a') as fs:
            fs.write(f"{job_id},submitted,{job_id}.jpeg\n")
    
    def job_status(self, job_id):
        if job_id in self.jobs:
            return self.jobs[job_id]["status"]
        return "job not found"
    
    def job_data(self, job_id):
        response = {"id": "", "status": "", "image": ""}
        if job_id in self.jobs:
            job = self.jobs[job_id]
            response["id"] = job_id
            response["status"] = job[job_id]["status"]
            response["image"] = job[job_id]["image"]

        return response
    
    def get_image(self, job_id, image_name):
        return 