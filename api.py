from flask import Flask, request
from PIL import Image
import numpy as np
import cv2
import base64
import os
import uuid

class ApplicationLayer():
    def __init__(self):
        self.image_folder = "images"
        os.makedirs(self.image_folder, exist_ok=True)

        self.jobs = []
        os.makedirs("jobs", exist_ok=True)
        if os.path.exists("jobs/jobs.csv"):
            with open("jobs/jobs.csv", 'r') as fs:
                line = fs.readline()
                while line:
                    info = line.replace(" ", "").split(",")
                    self.jobs.append({"id": info[0], "status": info[1], "image": info[2]})
                    line = fs.readline()

    def submit_job(self, file):
        guid = str(uuid.uuid4())
        with open(f'images/{guid}.jpeg', 'wb') as fs:
            fs.write(file)

        self.record_job(guid)

        return guid
    
    def record_job(self, job_id):
        with open("jobs/jobs.csv", 'a') as fs:
            fs.write(f"{job_id},submitted,{job_id}.jpeg\n")
    
    def job_status(self, job_id):
        for job in self.jobs:
            if job["id"] == job_id:
                return job["status"]
        return "job not found"

def create_app(name, application_layer=None):
    server = Flask(name)
    
    @server.route('/dl/segmentation', methods=['PUT'])
    def submit_segmentation_job():
        req = request
        if application_layer:
            return application_layer.submit_job(request.files['image'].read())
        else:
            return "error"
        
    @server.route('/job/status', methods=['GET'])
    def get_job_status():
        job_id = request.json['job_id']
        return application_layer.job_status(job_id)
        
    return server

  


if __name__ == '__main__':
    app = create_app(__name__)
    app.run(host="10.0.1.20", port=5000)
