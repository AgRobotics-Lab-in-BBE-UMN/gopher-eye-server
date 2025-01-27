from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import firebase_admin
from firebase_admin import credentials
from .util import getPostgresURI

db = SQLAlchemy()

def create_app():
    #Initialize the firebase application
    cred = credentials.Certificate('creds/firebase.json')
    firebase_admin.initialize_app(cred)

    app = Flask(__name__, instance_relative_config=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = getPostgresURI()

    db.init_app(app)

    with app.app_context():
        from . import routes
        
        db.create_all()

        return app
