from fastapi import FastAPI
from app.routers import auth, members

app = FastAPI(title="CSC Backend")

app.include_router(auth.router)
app.include_router(members.router)

@app.get("/")
def root():
    return {"message": "CSC Backend API läuft 🚀"}