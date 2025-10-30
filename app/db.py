import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/csc_db")
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=SQL_ECHO)

# Create session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base model for all ORM classes
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

# FastAPI dependency
def get_db():
    """Yields a database session for request handling."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
