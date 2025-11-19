from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

# 1. Create SQLAlchemy engine
# Verwende settings direkt, um unnötige Zwischenvariablen zu vermeiden
engine = create_engine(
    settings.DATABASE_URL, 
    echo=settings.SQL_ECHO, 
    future=True # SQLAlchemy 2.0 Stil
)

# 2. Create session factory
SessionLocal = sessionmaker(
    bind=engine, 
    autoflush=False, 
    autocommit=False, 
    future=True # SQLAlchemy 2.0 Stil
)

# 3. Base model for all ORM classes
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

# 4. FastAPI dependency
def get_db():
    """Yields a database session for request handling (Dependency Injection)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()