from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, members

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

# --- Healthcheck / Root ---
@app.get("/", tags=["Root"])
def root():
    return {"message": "CSC Backend API läuft 🚀"}
