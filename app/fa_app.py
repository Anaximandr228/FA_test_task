import uvicorn as uvicorn
from fastapi import FastAPI

from app import models
from app.database import SessionLocal, engine

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
