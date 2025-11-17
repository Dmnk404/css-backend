import os
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, get_db

# Test-Umgebung laden
load_dotenv(".env.test")

# Nutzt den PostgreSQL Test-Container
DATABASE_URL = os.getenv("DATABASE_URL")


@pytest.fixture(scope="session")
def engine():
    """Create test PostgreSQL engine."""
    engine = create_engine(DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def setup_database(engine):
    """Create tables before session starts and drop them afterwards."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine, setup_database):
    """
    Creates a NEW transaction for every test and rolls back afterward.
    Ensures isolation.
    """
    connection = engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=connection
    )

    session = TestingSessionLocal()

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield session

    transaction.rollback()
    connection.close()

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="function")
def client(db_session):
    """Provides a fastapi test client with DB override."""
    with TestClient(app) as c:
        yield c
