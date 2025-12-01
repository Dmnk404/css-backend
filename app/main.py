import os
import subprocess
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, members, password_reset


# --- Startup/Shutdown Logic ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run migrations and seed on startup (production only)"""
    if os.getenv("ENVIRONMENT") == "production":
        try:
            print("🔧 Running database migrations...")
            subprocess.run(["alembic", "upgrade", "head"], check=True, timeout=60)

            print("🌱 Running seed script...")
            subprocess.run(["python", "app/scripts/seed.py"], check=True, timeout=30)

            print("✅ Startup tasks completed!")
        except subprocess.TimeoutExpired:
            print("⚠️ Startup tasks timed out, continuing anyway...")
        except Exception as e:
            print(f"⚠️ Startup tasks failed: {e}, continuing anyway...")

    yield  # App läuft

    # Cleanup beim Shutdown (falls nötig)
    print("👋 Shutting down...")


app = FastAPI(title="CSC Backend", version="1.0. 0", lifespan=lifespan)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Router einbinden ---
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(members.router, prefix="/members", tags=["Members"])
app.include_router(
    password_reset.router, prefix="/auth", tags=["Authentication & Password Reset"]
)


# --- Healthcheck / Root ---
@app.api_route("/", methods=["GET", "HEAD"], tags=["Root"])
def root():
    return {"message": "CSC Backend API läuft 🚀"}


# Für lokale Entwicklung
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
