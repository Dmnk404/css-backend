import logging
import os
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, UTC, timezone

from app.db.database import get_db
# NEU: Service importieren
from app.services.password_reset_service import get_password_reset_service, PasswordResetService
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken
from app.core.security import (
    generate_reset_token,
    hash_reset_token,
    get_password_hash,
)
from app.schemas.common import PasswordResetRequest, PasswordReset

ACCESS_TOKEN_EXPIRE_MINUTES = 15
router = APIRouter(tags=["Authentication & Password Reset"])  # Prefix `/auth` wird in main.py gesetzt
logger = logging.getLogger(__name__)


@router.post("/forgot-password", status_code=200)
def forgot_password(
        email_request: PasswordResetRequest,
        background_tasks: BackgroundTasks = None,
        # NEU: Service-Dependency injizieren
        service: PasswordResetService = Depends(get_password_reset_service)
):
    """
    Initiates the password reset process by generating a token and simulating sending an email.
    """

    # Logik an den Service delegieren
    result_message = service.initiate_reset(
        email=email_request.email,
        background_tasks=background_tasks
    )

    if os.getenv("TESTING") == "1":
        return {
            "message": "Reset link sent (test mode).",
            "test_token": result_message
        }

    return {"message": result_message}


@router.post("/reset-password", status_code=200)
def reset_password(
        reset_data: PasswordReset,
        # NEU: Service-Dependency injizieren
        service: PasswordResetService = Depends(get_password_reset_service)
):
    """
    Validate a reset token and update the user's password.
    """

    # Logik an den Service delegieren
    user = service.finalize_reset(reset_data)

    print(f"✅ Password successfully reset for: {user.email}")

    return {"message": "Password successfully reset."}