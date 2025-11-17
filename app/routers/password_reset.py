import logging
import os
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, UTC, timezone

from app.db import get_db
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken
from app.core.security import (
    generate_reset_token,
    hash_reset_token,
    get_password_hash,
)
from app.schemas.common import EmailRequest, PasswordReset

ACCESS_TOKEN_EXPIRE_MINUTES = 15
router = APIRouter(prefix="/auth", tags=["Authentication & Password Reset"])
logger = logging.getLogger(__name__)


@router.post("/forgot-password", status_code=200)
def forgot_password(
    email_request: EmailRequest,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    user = db.query(User).filter(User.email == email_request.email).first()

    # Sicherheit: gleiche Antwort, egal ob User existiert
    if not user:
        return {"message": "If the email exists, a reset link has been sent."}

    cleartext_token = generate_reset_token()
    hashed_token = hash_reset_token(cleartext_token)
    expires_at = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Alte Resets löschen
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id
    ).delete()
    db.commit()

    new_token = PasswordResetToken(
        hashed_token=hashed_token,
        user_id=user.id,
        expires_at=expires_at
    )
    db.add(new_token)
    db.commit()
    db.refresh(new_token)

    print(f"🔑 RESET TOKEN (plaintext): {cleartext_token}")
    print(f"📅 Expires at: {expires_at}")

    if background_tasks:
        background_tasks.add_task(
            print,
            f"SIMULATED EMAIL: Password reset link for {user.email}: /auth/reset-password?token={cleartext_token}"
        )

    # 🚨 TESTMODUS: Echten Token zurückgeben
    if os.getenv("TESTING") == "1":
        return {
            "message": "Reset link sent (test mode).",
            "test_token": cleartext_token
        }

    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/reset-password", status_code=200)
def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    """
    Validate a reset token and update the user's password.
    """
    search_hash = hash_reset_token(reset_data.token)
    reset_token_entry = db.query(PasswordResetToken).filter(
        PasswordResetToken.hashed_token == search_hash
    ).first()

    if not reset_token_entry:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link.")

    aware_expires_at = reset_token_entry.expires_at.replace(tzinfo=timezone.utc)
    if aware_expires_at < datetime.now(timezone.utc):
        db.delete(reset_token_entry)
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired reset link.")

    user = reset_token_entry.user
    new_hashed_password = get_password_hash(reset_data.new_password)
    user.hashed_password = new_hashed_password

    db.delete(reset_token_entry)
    db.commit()
    db.refresh(user)

    print(f"✅ Password updated for: {user.email}")
    print(f"🔐 New hash: {user.hashed_password[:20]}...")

    return {"message": "Password successfully reset."}
