import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from alembic.config import Config
from alembic import command as alembic_command

from app.main import app
from app.db import Base, get_db

# --- 1. Temporäre Test-DB initialisieren ---

# Pfad zur Alembic-Konfigurationsdatei (vom Wurzelverzeichnis des Projekts aus)
ALEMBIC_CONFIG = "alembic.ini"
DATABASE_URL = "sqlite:///./test.db" # Verwende eine Datei oder :memory: für In-Memory

# SQLAlchemy Engine für die Tests
@pytest.fixture(scope="session")
def engine():
    return create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


# --- 2. Datenbankstruktur erstellen und Migrationen anwenden ---

@pytest.fixture(scope="session")
def setup_database(engine):  # <-- erhält das Engine-Objekt
    # ... (Der Alembic Code bleibt hier gleich, da er 'engine' erhält)
    alembic_cfg = Config(ALEMBIC_CONFIG)
    alembic_cfg.set_main_option("sqlalchemy.url", engine.url)  # Korrigiert: Nutze engine.url

    # Wende alle Alembic-Migrationen an...
    alembic_command.upgrade(alembic_cfg, "head")

    yield
    # ... (Aufräumen bleibt gleich)
    Base.metadata.drop_all(engine)


# --- 3. Überschreiben der Datenbank-Dependency (NEU & KORREKT) ---

@pytest.fixture(scope="function")
def db_session(setup_database, engine):  # <-- erhält das Engine-Objekt

    # Definiere die SessionMaker LOKAL, gebunden an die Engine
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Überschreibe die get_db Dependency in der App für diesen Test
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    yield session  # Der Test läuft hier

    # Teardown
    transaction.rollback()  # Rollback, um DB für den nächsten Test zu säubern
    session.close()
    connection.close()

    # Setze die Dependency in der App zurück
    app.dependency_overrides.pop(get_db)


# --- 4. Erstelle den TestClient (Beachte die Abhängigkeit von db_session) ---

@pytest.fixture(scope="function")
def client():
    """Stellt einen FastAPI TestClient zur Verfügung."""
    with TestClient(app) as c:
        yield c

    # Setze die Dependency zurück, falls du die echte DB in anderen Kontexten nutzen möchtest
    app.dependency_overrides.pop(get_db, None)