from fastapi import Depends, HTTPException, status
from app.models.user import User
# Wir importieren die get_current_user Funktion aus dem Auth Router
from app.routers.auth import get_current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency, die prüft, ob der eingeloggte Benutzer die Rolle 'Admin' hat.

    Raises HTTPException 403 FORBIDDEN, falls die Rolle nicht 'Admin' ist.
    Gibt das Benutzerobjekt zurück, falls die Autorisierung erfolgreich war.
    """
    # Prüft, ob der Benutzer eine Rolle und ob der Rollenname 'Admin' ist.
    # Da die Rolle über Alembic Seeding den Namen 'Admin' erhalten hat, ist dies die Quelle der Wahrheit.
    if current_user.role and current_user.role.name == "Admin":
        return current_user

    # Wird ausgelöst, wenn die Rolle nicht 'Admin' oder gar nicht vorhanden ist.
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Sie haben keine Berechtigung, diese Aktion durchzuführen. Nur Administratoren sind erlaubt.",
        headers={"WWW-Authenticate": "Bearer"},
    )