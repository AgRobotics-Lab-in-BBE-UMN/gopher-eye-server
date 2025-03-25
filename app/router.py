from fastapi import APIRouter, HTTPException, Request, UploadFile, Form, Depends
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
from app.config import get_firebase_user_from_token
from typing import Annotated
from app.repositories.user_repo import UserRepository
from app.models import User
from datetime import datetime, timezone


class Router(APIRouter):
    def __init__(self, application_layer=None, **kwargs):
        super().__init__(**kwargs)
        self.application_layer = application_layer


def create_api(name, application_layer=None, **kwargs):
    router = Router(application_layer=application_layer, **kwargs)

    @router.post("/register")
    async def register(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
        user_id = user["user_id"]
        try:
            # UserRepository.get_by_id(user_id)
            return JSONResponse({"status": "User already exists"})
        except:
            # new_user = User(
            #     id=user_id,
            #     email=user["email"],
            #     join_date=datetime.now(timezone.utc).date(),
            #     last_login=datetime.now(timezone.utc).date(),
            # )
            # UserRepository.create(new_user)
            return JSONResponse({"status": "User registered successfully"})
        return JSONResponse({"status": "ok"})

    # @app.put("/dl/segmentation")
    # async def segment_plant(image: UploadFile):
    #     if image.content_type != "multipart/form-data":
    #         raise HTTPException(status_code=400, detail="Invalid content type")
    #     return JSONResponse(
    #         {
    #             "plant_id": application_layer.segment_plant(
    #                 await image.read()
    #             )
    #         }
    #     )

    # @app.put("/dl/segmentation_spike")
    # async def segment_spike(image: UploadFile):
    #     if image.content_type != "multipart/form-data":
    #         raise HTTPException(status_code=400, detail="Invalid content type")
    #     return JSONResponse(
    #         {
    #             "plant_id": application_layer.segment_plant(
    #                 await image.read(),
    #                 task="spike"
    #             )
    #         }
    #     )

    # @app.put("/perf/segmentation")
    # async def perf_test_segmentation(image: UploadFile):
    #     if image.content_type != "multipart/form-data":
    #         raise HTTPException(status_code=400, detail="Invalid content type")
    #     plant_id = application_layer.segment_plant(await image.read())
    #     image_data, mimetype = application_layer.get_image(plant_id, "segmentation")
    #     return FileResponse(image_data, media_type=mimetype)

    # @app.get("/plant/status")
    # async def get_plant_status(plant_id: str):
    #     return JSONResponse({"status": application_layer.plant_status(plant_id)})

    # @app.get("/plant/data")
    # async def get_plant_data(plant_id: str):
    #     return JSONResponse(application_layer.plant_data(plant_id))

    # @app.get("/plant/image")
    # async def get_plant_item(plant_id: str, image_name: str):
    #     image_data, mimetype = application_layer.get_image(plant_id, image_name)
    #     if image_data:
    #         return FileResponse(image_data, media_type=mimetype)
    #     else:
    #         raise HTTPException(status_code=400, detail="Invalid request")

    # @app.get("/plant/ids")
    # async def get_plant_ids():
    #     return JSONResponse({"plant_ids": application_layer.get_plant_ids()})

    # @app.post("/otpVerification")
    # async def verify_otp(status: Optional[str] = Form(...)):
    #     if status == "200":
    #         return JSONResponse(
    #             {
    #                 "status": 200,
    #                 "message": "OTP verified successfully",
    #                 "token": "test_token",
    #             }
    #         )
    #     elif status == "201":
    #         return JSONResponse(
    #             {
    #                 "status": 201,
    #                 "message": "OTP verified successfully",
    #                 "token": "test_token",
    #             }
    #         )
    #     elif status == "401":
    #         raise HTTPException(status_code=401, detail="OTP is not valid")
    #     else:
    #         return JSONResponse(
    #             {
    #                 "status": 200,
    #                 "message": "OTP verified successfully",
    #                 "token": "test_token",
    #             }
    #         )

    # @app.post("/signin")
    # async def signin(status: Optional[str] = Form(...)):
    #     if status == "200":
    #         return JSONResponse(
    #             {
    #                 "status": 200,
    #                 "message": "login successfully",
    #                 "token": "test_token",
    #             }
    #         )
    #     elif status == "201":
    #         return JSONResponse(
    #             {
    #                 "status": 201,
    #                 "message": "login successfully",
    #                 "token": "test_token",
    #             }
    #         )
    #     elif status == "401":
    #         raise HTTPException(
    #             status_code=401,
    #             detail="email or password is wrong/something went wrong",
    #         )
    #     else:
    #         return JSONResponse(
    #             {
    #                 "status": 200,
    #                 "message": "login successfully",
    #                 "token": "test_token",
    #             }
    #         )

    # @app.get("/status")
    # async def get_status():
    #     return JSONResponse({"status": "ok"})

    return router
