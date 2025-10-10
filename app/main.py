from fastapi import FastAPI
from app.routers import members

app = FastAPI(title="CSC Backend API")

app.include_router(members.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the CSC Backend API"}
