from fastapi import FastAPI
from app.db import Base, engine
from app.routers import auth, members

# Datenbanktabellen erstellen, falls sie noch nicht existieren
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CSC Backend")

# Router registrieren
app.include_router(auth.router)
app.include_router(members.router)

@app.get("/")
def root():
    return {"message": "CSC Backend API läuft 🚀"}
