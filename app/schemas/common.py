from pydantic import BaseModel, EmailStr, Field

class EmailRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    """Schema für die Eingabe des Reset-Tokens und des neuen Passworts."""
    token: str = Field(..., description="Der Klartext-Reset-Token aus der E-Mail.")
    new_password: str = Field(..., min_length=8, description="Das neue Passwort des Benutzers (mindestens 8 Zeichen).")