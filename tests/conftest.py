import os
import sys
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Ensure project root is visible for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.db.database import get_db, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role
from app.models.member import Member


# -------------------------------------------------------
# Test database setup (SQLite in-memory)
# -------------------------------------------------------

TEST_DB_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Tabellen erstellen
Base.metadata.create_all(bind=engine)

# ✅ WICHTIG: Rollen EINMAL initialisieren (nicht in jeder Session)
def init_roles():
    """Initialize default roles once."""
    db = TestingSessionLocal()
    try:
        # Prüfen ob Rollen bereits existieren
        existing_roles = db.query(Role).count()
        if existing_roles == 0:
            db.add_all([
                Role(id=1, name="Admin", description="Administrator"),
                Role(id=2, name="User", description="Standard application user")
            ])
            db.commit()
    finally:
        db.close()

# Rollen beim Import initialisieren
init_roles()


# -------------------------------------------------------
# DB fixtures
# -------------------------------------------------------

@pytest.fixture(scope="function")
def db_session():
    """Provides a clean database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Nur User und Member Tables cleanen, NICHT Roles!
    session.query(User).delete()
    session.query(Member).delete()
    session.commit()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# -------------------------------------------------------
# Dependency override for FastAPI
# -------------------------------------------------------

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient using overridden DB."""
    with TestClient(app) as c:
        yield c


# -------------------------------------------------------
# Utility: user creation
# -------------------------------------------------------

def create_test_user(session: Session, username: str, email: str, role_name: str, password: str = "pass"):
    role = session.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise ValueError(f"Role '{role_name}' not found.")

    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        role_id=role.id,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# -------------------------------------------------------
# Auth fixtures
# -------------------------------------------------------

@pytest.fixture(scope="function")
def admin_token(client: TestClient, db_session: Session):
    create_test_user(db_session, "adminuser", "admin@test.com", "Admin", "adminpass")

    login = {"username": "adminuser", "password": "adminpass", "grant_type": "password"}
    response = client.post("/auth/login", data=login)

    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def member_token(client: TestClient, db_session: Session):
    create_test_user(db_session, "memberuser", "member@test.com", "User", "memberpass")

    login = {"username": "memberuser", "password": "memberpass", "grant_type": "password"}
    response = client.post("/auth/login", data=login)

    assert response.status_code == 200
    return response.json()["access_token"]


# -------------------------------------------------------
# Member fixture (example entry)
# -------------------------------------------------------

@pytest.fixture(scope="function")
def existing_member_id(db_session: Session):
    member = Member(
        name="Sample Member",
        birth_date=date(1990, 5, 20),
        email="sample@member.com",
        phone="123456789",
        address="Test Street",  # ✅ Korrigiert: address statt street
        postal_code="12345",    # ✅ Korrigiert: postal_code statt zip_code
        city="Test City",
        # country entfernt, da nicht im Model
        active=True,  # ✅ Korrigiert: active statt is_active
    )
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)
    return member.id