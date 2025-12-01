import os
import sys
from datetime import date
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure project root is visible for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.security import get_password_hash
from app.db import Base, get_db
from app.main import app
from app.models.member import Member
from app.models.role import Role
from app.models.user import User

# -------------------------------------------------------
# Test database setup (SQLite in-memory)
# -------------------------------------------------------

TEST_DB_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Session factory used both by transactional db_session fixture and by direct helper sessions
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Create all tables once for the in-memory DB
Base.metadata.create_all(bind=engine)


# Initialize roles once
def init_roles() -> None:
    db = TestingSessionLocal()
    try:
        existing_roles = db.query(Role).count()
        if existing_roles == 0:
            db.add_all(
                [
                    Role(id=1, name="Admin", description="Administrator"),
                    Role(id=2, name="User", description="Standard application user"),
                ]
            )
            db.commit()
    finally:
        db.close()


init_roles()


# -------------------------------------------------------
# DB fixtures
# -------------------------------------------------------


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Provides a clean database session for each test.
    Uses a transaction/connection pattern so tests are isolated.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Clean only Users and Members between tests to keep Roles stable
    session.query(User).delete()
    session.query(Member).delete()
    session.commit()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


# -------------------------------------------------------
# Dependency override for FastAPI (TestClient -> test DB)
# -------------------------------------------------------


def override_get_db() -> Generator[Session, None, None]:
    """
    Default override returns a new session bound to engine.
    Note: db_session fixture uses a connection-bound session inside a transaction.
    Tests that need the TestClient to see data created by fixtures must create those rows
    in a separate session (see admin_user/admin_token below).
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """FastAPI TestClient using overridden DB."""
    with TestClient(app) as c:
        yield c


# -------------------------------------------------------
# Utility: user creation (helper that uses an independent session)
# -------------------------------------------------------


def create_test_user_direct(
    session: Session, username: str, email: str, role_name: str, password: str = "pass"
) -> User:
    """
    Create a user in the given session and commit. This helper is intended
    to be used with a fresh session (TestingSessionLocal()), not the transactional db_session fixture.
    """
    role = session.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise ValueError(f"Role '{role_name}' not found.")

    user = session.query(User).filter_by(username=username).first()
    if user:
        return user

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
# Auth fixtures (admin and member)
# -------------------------------------------------------


@pytest.fixture(scope="function")
def admin_user() -> User:
    """
    Create/return an admin user using an independent session (visible to TestClient).
    Use this fixture in tests needing the User object.
    """
    session = TestingSessionLocal()
    try:
        return create_test_user_direct(
            session, "adminuser", "admin@test.com", "Admin", "adminpass"
        )
    finally:
        session.close()


@pytest.fixture(scope="function")
def member_user() -> User:
    session = TestingSessionLocal()
    try:
        return create_test_user_direct(
            session, "memberuser", "member@test.com", "User", "memberpass"
        )
    finally:
        session.close()


@pytest.fixture(scope="function")
def admin_token(client: TestClient) -> str:
    """
    Ensure an admin user exists (created in an independent session) and obtain a valid JWT via the real login endpoint.
    Creating the user via a fresh session (TestingSessionLocal) makes it immediately visible to the TestClient.
    """
    session = TestingSessionLocal()
    try:
        create_test_user_direct(
            session, "adminuser", "admin@test.com", "Admin", "adminpass"
        )
    finally:
        session.close()

    login = {"username": "adminuser", "password": "adminpass", "grant_type": "password"}
    response = client.post("/auth/login", data=login)
    assert (
        response.status_code == 200
    ), f"Login in fixture failed: {response.status_code} {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def member_token(client: TestClient) -> str:
    session = TestingSessionLocal()
    try:
        create_test_user_direct(
            session, "memberuser", "member@test.com", "User", "memberpass"
        )
    finally:
        session.close()

    login = {
        "username": "memberuser",
        "password": "memberpass",
        "grant_type": "password",
    }
    response = client.post("/auth/login", data=login)
    assert (
        response.status_code == 200
    ), f"Login in fixture failed: {response.status_code} {response.text}"
    return response.json()["access_token"]


# -------------------------------------------------------
# Member fixture (example entry)
# -------------------------------------------------------


@pytest.fixture(scope="function")
def existing_member_id(db_session: Session) -> int:
    member = Member(
        name="Sample Member",
        birth_date=date(1990, 5, 20),
        email="sample@member.com",
        phone="123456789",
        address="Test Street",
        postal_code="12345",
        city="Test City",
        active=True,
    )
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)
    return member.id
