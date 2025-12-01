from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    ENVIRONMENT: str = Field(default="development")

    APP_HOST: str = "0. 0.0.0"
    APP_PORT: int = 8000
    APP_DEBUG: bool = False

    # ========================
    # 2. Datenbank-Einstellungen (PostgreSQL)
    # ========================
    # WICHTIG: Optional für Render (wird zur Laufzeit gesetzt)
    DATABASE_URL: str = Field(
        default="postgresql://user:pass@localhost:5432/db"  # Fallback für lokale Entwicklung
    )

    SQL_ECHO: bool = False

    # ========================
    # 3. Sicherheits-Einstellungen (JWT & Auth)
    # ========================
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-min-32-chars-please"
    )

    SECURITY_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60

    # ========================
    # 4. Mail-Einstellungen (Optional)
    # ========================
    MAIL_SERVER: Optional[str] = None
    MAIL_PORT: Optional[int] = None
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None

    # ========================
    # Pydantic Konfiguration
    # ========================
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Erstellen einer globalen Instanz, die importiert und im gesamten Projekt verwendet wird
settings = Settings()
