from fastapi import HTTPException, status
from sqlalchemy.exc import (
    NoResultFound,  # Neu hinzugefügt für präzisere Fehlerbehandlung
)
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate


class UserService:
    """Service-Klasse zur Kapselung der Geschäftslogik für Benutzer."""

    # ----------------------------------------------------
    # HILFSFUNKTION: Standardrolle abrufen (User)
    # ----------------------------------------------------
    def get_default_role(self, db: Session) -> Role:
        """Sucht die Standardrolle ('User') in der Datenbank."""
        try:
            # ⚠️ KORREKTUR: Suche nach "User" (Großschreibung)
            role = db.query(Role).filter(Role.name == "User").one()
            return role
        except NoResultFound:
            # Dies ist die Fehlermeldung, die der Test 500 ausgelöst hat!
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Standardrolle 'User' nicht in der Datenbank gefunden. Bitte Datenbank-Seeding prüfen.",
            )

    # ----------------------------------------------------
    # KERN-LOGIK: Benutzer registrieren
    # ----------------------------------------------------
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """Erstellt einen neuen Benutzer und weist ihm die Standardrolle zu."""

        # 1. Prüfen auf existierenden Benutzer (Username ODER E-Mail)
        existing_user = (
            db.query(User)
            .filter(
                (User.username == user_data.username) | (User.email == user_data.email)
            )
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,  # Besser als 400 für Duplikate
                detail="Username or email is already taken",
            )

        # 2. Rolle abrufen (Geschäftsregel)
        # 🚨 HIER LÖSEN WIR DEN 500-FEHLER: Die Methode sucht nun nach dem korrekten Namen "User"
        default_role = self.get_default_role(db)

        # 3. Passwort hashen
        hashed_pw = get_password_hash(user_data.password)

        # 4. Benutzer erstellen
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_pw,
            role_id=default_role.id,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user


# Globales Service-Objekt für Dependency Injection
user_service = UserService()
