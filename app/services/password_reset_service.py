import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import generate_reset_token, get_password_hash, hash_reset_token
from app.db import get_db
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.schemas.common import PasswordReset

ACCESS_TOKEN_EXPIRE_MINUTES = 15
logger = logging.getLogger(__name__)


class PasswordResetService:
    """
    Kapselt die Geschäftslogik für den Passwort-Reset-Prozess.
    """

    def __init__(self, db: Session):
        self.db = db

    def initiate_reset(
        self, email: str, background_tasks: Optional[BackgroundTasks] = None
    ) -> str:
        """
        Startet den Reset-Prozess: generiert Token, speichert Hash und simuliert E-Mail-Versand.
        Gibt den Klartext-Token (nur im Testmodus) zurück.
        """
        user = self.db.query(User).filter(User.email == email).first()

        # Sicherheit: Keine Unterscheidung, ob User existiert
        if not user:
            return "If the email exists, a reset link has been sent."

        cleartext_token = generate_reset_token()
        hashed_token = hash_reset_token(cleartext_token)
        # Verwenden Sie UTC für Zeitzonenkonformität
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

        # Alte Resets für diesen Benutzer löschen
        self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id
        ).delete()
        self.db.commit()

        # Neuen Token speichern
        new_token = PasswordResetToken(
            hashed_token=hashed_token, user_id=user.id, expires_at=expires_at
        )
        self.db.add(new_token)
        self.db.commit()
        self.db.refresh(new_token)

        # Simulation: E-Mail-Versand
        if background_tasks:
            background_tasks.add_task(
                logger.info,
                f"SIMULATED EMAIL: Password reset link for {user.email}: /auth/reset-password?token={cleartext_token}",
            )

        # Nur für lokale Tests/Debugging: Den echten Token zurückgeben
        if os.getenv("TESTING") == "1":
            print(f"🔑 RESET TOKEN (plaintext): {cleartext_token}")
            return cleartext_token

        return "If the email exists, a reset link has been sent."

    def finalize_reset(self, reset_data: PasswordReset) -> User:
        """
        Validiert den Reset-Token und aktualisiert das Benutzerpasswort.
        """
        search_hash = hash_reset_token(reset_data.token)
        reset_token_entry = (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.hashed_token == search_hash)
            .first()
        )

        if not reset_token_entry:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ungültiger oder abgelaufener Reset-Link.",
            )

        # Zeitzonenvergleich: Muss mit UTC verglichen werden
        if reset_token_entry.expires_at.replace(tzinfo=timezone.utc) < datetime.now(
            timezone.utc
        ):
            self.db.delete(reset_token_entry)
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ungültiger oder abgelaufener Reset-Link.",
            )

        # Passwort aktualisieren
        user = reset_token_entry.user
        new_hashed_password = get_password_hash(reset_data.new_password)
        user.hashed_password = new_hashed_password

        # Token löschen
        self.db.delete(reset_token_entry)
        self.db.commit()
        self.db.refresh(user)

        return user


# Dependency, um den Service in den Routern zu injizieren
def get_password_reset_service(db: Session = Depends(get_db)) -> PasswordResetService:
    return PasswordResetService(db)
