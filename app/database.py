from sqlalchemy import create_engine, String, Column, Date, Mode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.util import getPostgresURI
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from typing import Any


class SQLAlchemy:
    SQLALCHEMY_DATABASE_URL = getPostgresURI()
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def __getattr__(self, name: str) -> Any:
        for mod in (sa, sa_orm):
            if hasattr(mod, name):
                return getattr(mod, name)

        raise AttributeError(name)
    
    