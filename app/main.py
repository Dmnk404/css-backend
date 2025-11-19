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
app.include_router(password_reset.router, prefix="/auth", tags=["Authentication & Password Reset"])

# --- Healthcheck / Root ---
@app.get("/", tags=["Root"])
def root():
    return {"message": "CSC Backend API läuft 🚀"}