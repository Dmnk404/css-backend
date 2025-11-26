from app.db import Base, engine


def init():
    print("Running DB initialization...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialization complete")


if __name__ == "__main__":
    init()
