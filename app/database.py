from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.util import getPostgresURI
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from typing import Any

SQLITE_DATABASE_URL = getPostgresURI()

engine = create_engine(SQLITE_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
