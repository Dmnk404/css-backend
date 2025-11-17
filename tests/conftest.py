import os
import uuid
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from app.main import app
from app.db import Base, get_db


# Load the .env.test file
load_dotenv(".env.test")

DATABASE_URL = os.getenv("DATABASE_URL")
assert DATABASE_URL, "DATABASE_URL missing in .env.test"


@pytest.fixture(scope="session")
def engine():
    """
    Create a shared PostgreSQL engine for the entire testsuite.
    Schema isolation happens on a per-test basis.
    """
    engine = create_engine(
        DATABASE_URL,
        future=True,
        pool_pre_ping=True
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_schema(engine):
    """
    Creates a new PostgreSQL SCHEMA for each test.
    Runs all tables inside that schema.
    Cleans up the schema afterward.
    """
    schema_name = f"test_schema_{uuid.uuid4().hex[:8]}"

    # Create schema
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA {schema_name};"))
        conn.commit()

    # Monkeypatch metadata to use the new schema
    original_schema = Base.metadata.schema
    Base.metadata.schema = schema_name

    # Create tables inside the schema
    Base.metadata.create_all(engine)

    yield schema_name

    # Clean up the schema after the test
    with engine.connect() as conn:
        conn.execute(text(f"DROP SCHEMA {schema_name} CASCADE;"))
        conn.commit()

    # Restore original schema
    Base.metadata.schema = original_schema


@pytest.fixture(scope="function")
def db_session(engine, db_schema):
    """
    Create a fresh DB session for each test using the test schema.
    Uses SAVEPOINT-style rollbacks for strong isolation.
    """
    connection = engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(
        bind=connection,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        future=True,
    )

    session = TestingSessionLocal()

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield session

    # rollback test changes
    transaction.rollback()
    connection.close()

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI test client bound to the isolated test DB."""
    with TestClient(app) as c:
        yield c
