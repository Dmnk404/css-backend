from fastapi import FastAPI
from app.routers import members
from app.db import Base, engine
from app.models.member import Member
app = FastAPI(title="CSC Backend API")

Base.metadata.create_all(bind=engine)
app.include_router(members.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the CSC Backend API"}
