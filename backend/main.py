from fastapi import FastAPI

from app.database.database import Base, engine
from app.api.repository import router as repository_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CodePilot AI")

app.include_router(repository_router)


@app.get("/")
def root():
    return {"message": "CodePilot AI Backend"}