from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.role import Role  # Importieren Sie das Role Model
from app.schemas.user import UserCreate
from app.core.security import get_password_hash  # Hashing importieren


class UserService:
    """Service-Klasse zur Kapselung der Geschäftslogik für Benutzer."""

    # ----------------------------------------------------
    # HILFSFUNKTION: Standardrolle abrufen (MEMBER)
    # ----------------------------------------------------
    def get_default_role(self, db: Session) -> Role:
        """Sucht die Standardrolle ('Member') in der Datenbank."""
        # Wichtig: Die Role "Member" muss im Seeding-Skript erstellt werden!
        role = db.query(Role).filter(Role.name == "Member").first()
        if not role:
            # Dies sollte nur passieren, wenn das Seeding fehlschlägt
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Standardrolle 'Member' nicht in der Datenbank gefunden."
            )
        return role

    # ----------------------------------------------------
    # KERN-LOGIK: Benutzer registrieren
    # ----------------------------------------------------
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """Erstellt einen neuen Benutzer und weist ihm die Standardrolle zu."""

        # 1. Prüfen auf existierenden Benutzer
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is already taken",
            )

        # 2. Rolle abrufen (Geschäftsregel)
        default_role = self.get_default_role(db)

        # 3. Passwort hashen
        hashed_pw = get_password_hash(user_data.password)

        # 4. Benutzer erstellen
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_pw,
            # NEU: Role ID zuweisen
            role_id=default_role.id
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user


# Globales Service-Objekt für Dependency Injection
user_service = UserService()