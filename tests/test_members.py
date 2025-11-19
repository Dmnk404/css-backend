import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from app.db.database import Base, get_db
from app.models.user import User
from app.models.role import Role  # NEU: Role importieren
from app.core.security import get_password_hash
from app.main import app  # Import der Haupt-App

# ----------------------------------------------------------------------
# 🔹 DB Setup Fixture
# ----------------------------------------------------------------------

# Datenbank-URL für Tests (SQLite in memory)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def engine():
    # Wir verwenden eine Datei-DB, damit Alembic funktionieren kann
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    # Datenbank erstellen, falls sie nicht existiert
    if not database_exists(engine.url):
        create_database(engine.url)
    yield engine
    # Nach allen Tests (session scope) cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Bietet eine unabhängige Datenbank-Sitzung für jeden Test."""
    connection = engine.connect()
    transaction = connection.begin()

    # 1. Datenbank-Setup für den Test (Tabellen und Seeding)
    Base.metadata.create_all(bind=connection)

    # NEU: Manuelles Seeding der Rollen, da Alembic im TestClient-Setup nicht läuft
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    db = SessionLocal()

    # Rollen manuell seeden
    if not db.query(Role).filter(Role.name == "Admin").first():
        db.add(Role(id=1, name="Admin", description="Full access"))
        db.add(Role(id=2, name="Member", description="Standard member"))
        db.commit()

    # 2. Erstelle eine Session, die an die Transaktion gebunden ist
    session = SessionLocal(bind=connection)

    # 3. Überschreibe die get_db Dependency für den Test
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield session

    # 4. Rollback und Cleanup
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Stellt einen FastApi TestClient bereit."""
    return TestClient(app)


# ----------------------------------------------------------------------
# 🔹 Benutzer- und Token-Fixtures (Autorisierung)
# ----------------------------------------------------------------------

@pytest.fixture(scope="function")
def admin_user(db_session):
    """Erstellt einen Benutzer und weist ihm die Admin-Rolle zu."""
    admin_role = db_session.query(Role).filter(Role.name == "Admin").first()

    user = User(
        username="admin_test",
        email="admin@csc.de",
        hashed_password=get_password_hash("secureadminpw"),
        role_id=admin_role.id
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def member_user(db_session):
    """Erstellt einen Standard-Benutzer mit der Member-Rolle."""
    member_role = db_session.query(Role).filter(Role.name == "Member").first()

    user = User(
        username="member_test",
        email="member@csc.de",
        hashed_password=get_password_hash("securememberpw"),
        role_id=member_role.id
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def admin_token(client, admin_user):
    """Liefert das JWT für den Admin-Benutzer."""
    login_data = {"username": admin_user.username, "password": "secureadminpw", "grant_type": "password"}
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def member_token(client, member_user):
    """Liefert das JWT für den Standard-Mitglieds-Benutzer."""
    login_data = {"username": member_user.username, "password": "securememberpw", "grant_type": "password"}
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def existing_member_id(client, admin_token):
    """Erstellt ein Mitglied (NICHT User) und gibt dessen ID zurück."""
    member_data = {
        "name": "Member For Update",
        "birth_date": "2000-10-10",
        "email": "update@test.de"
    }
    response = client.post(
        "/members/",
        json=member_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    return response.json()["id"]