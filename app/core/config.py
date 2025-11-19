from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """
    Klasse zum Laden aller Anwendungseinstellungen aus Umgebungsvariablen
    oder der .env-Datei. Verwendet Pydantic BaseSettings.
    """

    # ========================
    # 1. Basis-Einstellungen (FastAPI / App Settings)
    # ========================
    PROJECT_NAME: str = "CSC-Backend"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development")  # Nützlich für Logs/Conditional Logic

    APP_HOST: str = "0.0.0.0"  # Host für Uvicorn
    APP_PORT: int = 8000  # Port für Uvicorn
    APP_DEBUG: bool = False  # True für Entwicklung

    # ========================
    # 2. Datenbank-Einstellungen (PostgreSQL)
    # ========================
    # Die Hauptverbindungs-URL, die alle Details aus der .env kombiniert (z.B. postgresql://user:pass@host:port/db)
    DATABASE_URL: str

    SQL_ECHO: bool = False  # Schaltet SQLAlchemy-Logging (SQL-Queries) an oder aus

    # ========================
    # 3. Sicherheits-Einstellungen (JWT & Auth)
    # ========================
    # Der geheime Schlüssel zum Signieren von JWT-Token - MUSS geheim gehalten werden!
    SECRET_KEY: str

    SECURITY_ALGORITHM: str = "HS256"

    # Gültigkeitsdauer des Access Tokens in Minuten (z.B. 60 * 24 = 24 Stunden)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Gültigkeitsdauer des Passwort-Reset-Tokens in Minuten
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60  # 1 Stunde

    # ========================
    # 4. Mail-Einstellungen (Optional)
    # ========================
    # Diese Felder sind optional, falls du sie später für Passwort-Resets o.ä. brauchst.
    MAIL_SERVER: Optional[str] = None
    MAIL_PORT: Optional[int] = None
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None

    # ========================
    # Pydantic Konfiguration
    # ========================
    model_config = SettingsConfigDict(
        case_sensitive=True,  # Variablen-Namen sind Groß-/Kleinschreibung-sensitiv
        env_file=".env",  # Einstellungen aus der .env-Datei laden
        extra="ignore"  # Unnötige Variablen (wie POSTGRES_USER, ALEMBIC_...) in .env ignorieren
    )


# Erstellen einer globalen Instanz, die importiert und im gesamten Projekt verwendet wird
settings = Settings()