import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, members, password_reset

app = FastAPI(title="CSC Backend", version="1.0.0")

# --- CORS (für lokale Entwicklung oder späteres Frontend) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # später spezifisch machen, z. B. ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Router einbinden ---
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(members.router, prefix="/members", tags=["Members"])
# FIX: Den Password Reset Router ebenfalls unter /auth mounten
app.include_router(
    password_reset.router, prefix="/auth", tags=["Authentication & Password Reset"]
)


# --- Healthcheck / Root ---
@app.api_route("/", methods=["GET", "HEAD"], tags=["Root"])  # GEÄNDERT: GET + HEAD
def root():
    return {"message": "CSC Backend API läuft 🚀"}


# NEU: Für Production (Render, Railway, etc.)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0. 0.0", port=port, reload=False)
