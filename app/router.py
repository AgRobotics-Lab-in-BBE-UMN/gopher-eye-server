import uuid
from fastapi import APIRouter, HTTPException, Request, Response, UploadFile, Form, Depends
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional

from pytest import Session
from app.config import get_firebase_user_from_token
from typing import Annotated
from app.database import get_db
from app.repositories.user_repo import UserRepository
from app.models import User
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.application_interface import ApplicationInterface


class Router(APIRouter):
    def __init__(self, application_layer=None, **kwargs):
        super().__init__(**kwargs)
        self.application_layer = application_layer


def create_api(name, application_layer:ApplicationInterface=None, **kwargs):
    router = Router(application_layer=application_layer, **kwargs)

    @router.post("/register")
    async def register(user: Annotated[dict, Depends(get_firebase_user_from_token)], db: Session = Depends(get_db)):
        try:
            user_id = user["user_id"]
            email = user["email"]
            user = User(id=user_id, email=email)
            
            application_layer.register_user(db, user)
            return JSONResponse({"status": "User registered successfully"})
        except application_layer.UserAlreadyExistsException:
            return JSONResponse({"status": "User already exists"})
        except Exception as e:
            print("Failed to register user: ", e)
            return HTTPException(status_code=500, detail="Failed to register user")
        
    @router.get("/records")
    async def get_records(user: Annotated[dict, Depends(get_firebase_user_from_token)],  db: Session = Depends(get_db)):
        try:
            user_id = user["user_id"]
            records = application_layer.get_user_records(db, user_id)
            return JSONResponse({"records": [record.id for record in records]})
        except Exception as e:
            print("Failed to fetch records: ", e)
            raise HTTPException(status_code=500, detail="Failed to fetch records")
        
    @router.put("/records/create")
    async def create_record(request: Request, user: Annotated[dict, Depends(get_firebase_user_from_token)], db: Session = Depends(get_db)):
        try:
            user_id = user["user_id"]
            try:
                body = await request.json()
            except:
                body = await request.form()
            site = body.get("site_id")
            
            record_id = application_layer.create_record(db, user_id, site)
            return JSONResponse({"status": f"Record created successfully", "record_id": record_id})
        except Exception as e:
            print("Failed to create record: ", e)
            raise HTTPException(status_code=500, detail="Failed to create record")
        
    @router.put("/records/{record_id}/samples/create")
    async def create_sample(request: Request, record_id: str, user: Annotated[dict, Depends(get_firebase_user_from_token)], db: Session = Depends(get_db)):
        try:
            user_id = user["user_id"]
            
            try:
                body = await request.json()
            except:
                body = await request.form()
                
            image_file = body.get("image")
            sample_type = body.get("sample_type")
            sample_id = application_layer.create_sample(db, user_id, record_id, image_file, sample_type)
            return JSONResponse({"status": f"Sample created successfully", "sample_id": sample_id})
        except Exception as e:
            print("Failed to create sample: ", e)
            raise HTTPException(status_code=500, detail="Failed to create sample")
        
    @router.get("/records/{record_id}/samples")
    async def get_samples(record_id: str, user: Annotated[dict, Depends(get_firebase_user_from_token)], db: Session = Depends(get_db)):
        try:
            user_id = user["user_id"]
            samples = application_layer.get_samples(db, user_id, record_id)
            response = {"samples": []}
            for sample in samples:
                sample_data = {
                    "id": sample.id,
                    "record_id": sample.record_id,
                    "created_date": str(sample.created_date),
                    "created_by": sample.created_by,
                    "image_url": sample.image_url,
                    "type": sample.type,
                    "processing_status": sample.processing_status
                }
                response["samples"].append(sample_data)
            return JSONResponse(response)
        except Exception as e:
            print("Failed to fetch samples: ", e)
            raise HTTPException(status_code=500, detail="Failed to fetch samples")

    @router.post("/segment/{sample_id}")
    async def segment_sample(sample_id: str, user: Annotated[dict, Depends(get_firebase_user_from_token)], db: Session = Depends(get_db)):
        try:
            user_id = user["user_id"]
            application_layer.segment_sample(db, sample_id)
            return JSONResponse({"status": "Sample segmentation started"})
        except Exception as e:
            print("Failed to segment sample: ", e)
            raise HTTPException(status_code=500, detail="Failed to segment sample")

    @router.get("/records/{record_id}/samples/{sample_id}/masks")
    async def get_masks(sample_id: str, user: Annotated[dict, Depends(get_firebase_user_from_token)], db: Session = Depends(get_db)):
        try:
            user_id = user["user_id"]
            masks = application_layer.get_masks(db, sample_id)
            result = {"masks": [
                {
                    "id": mask.id,
                    "sample_id": mask.sample_id,
                    "mask_url": mask.mask_url,
                    "type": mask.type,
                    "created_date": str(mask.created_date),
                    "created_by": mask.created_by
                } for mask in masks
            ]}
            return JSONResponse({"masks": masks})
        except Exception as e:
            print("Failed to fetch masks: ", e)
            raise HTTPException(status_code=500, detail="Failed to fetch masks")
        
    @router.get("/records/{record_id}/samples/{sample_id}/boxes")
    async def get_boxes(mask_id: str, user: Annotated[dict, Depends(get_firebase_user_from_token)], db: Session = Depends(get_db)):
        try:
            user_id = user["user_id"]
            boxes = application_layer.get_boxes(db, user_id, mask_id)
            return JSONResponse({"boxes": boxes})
        except Exception as e:
            print("Failed to fetch boxes: ", e)
            raise HTTPException(status_code=500, detail="Failed to fetch boxes")
    
    return router
