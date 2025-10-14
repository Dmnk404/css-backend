from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/csc_db"

engine = create_engine(DATABASE_URL, echo=True)

# Session-Klasse
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base-Klasse für Models
class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()