from fastapi import FastAPI
from app.router import create_api
from app.application import Application
import firebase_admin
from app.config import get_settings


app = FastAPI()
router = create_api(__name__, application_layer=Application())

app.include_router(router)
firebase_admin.initialize_app()
