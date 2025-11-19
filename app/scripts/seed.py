#!/usr/bin/env python3
"""
Seed script for css-backend.

- Creates Role 'Member' if it doesn't exist
- Creates an admin/test user (username: admin / password: adminpass) if not present
- Creates a few example Members

Usage:
  # inside container:
  python app/scripts/seed.py

  # or locally (ensure PYTHONPATH includes project root and env vars set):
  python app/scripts/seed.py
"""
from datetime import datetime
from app.db import SessionLocal
from app.core.security import get_password_hash
# Models import: Role is exported from app.models, User is in app.models.user, Member may be in app.models.member
try:
    from app.models import Role
except Exception:
    from app.models.role import Role  # fallback

try:
    from app.models.user import User
except Exception:
    from app.models import User  # fallback

# Try Member model imports (adjust per repo structure)
try:
    from app.models.member import Member
except Exception:
    try:
        from app.models import Member
    except Exception:
        Member = None

SEED_MEMBERS = [
    {"first_name": "Max", "last_name": "Mustermann", "email": "max@example.com", "notes": "Demo"},
    {"first_name": "Erika", "last_name": "Mustermann", "email": "erika@example.com", "notes": "Demo"},
    {"first_name": "Ada", "last_name": "Lovelace", "email": "ada@demo.org", "notes": "Demo"},
    {"first_name": "Alan", "last_name": "Turing", "email": "alan@demo.org", "notes": "Demo"},
]

def main():
    db = SessionLocal()
    try:
        # Ensure Role 'Member' exists
        role = db.query(Role).filter(Role.name == "Member").first()
        if not role:
            role = Role(name="Member")
            db.add(role)
            db.commit()
            db.refresh(role)
            print("Created Role 'Member'")

        # Ensure admin user exists
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("adminpass"),
                role=role
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("Created admin user (username=admin, password=adminpass)")

        # Create example members if Member model present
        if Member is None:
            print("Warning: Member model not found in app.models.member or app.models. Skipping seeding members.")
        else:
            existing = db.query(Member).count()
            if existing == 0:
                for m in SEED_MEMBERS:
                    obj = Member(
                        first_name=m["first_name"],
                        last_name=m["last_name"],
                        email=m["email"],
                        notes=m.get("notes", ""),
                        created_at=getattr(Member, "created_at", datetime.utcnow())
                    )
                    db.add(obj)
                db.commit()
                print(f"Seeded {len(SEED_MEMBERS)} example members")
            else:
                print(f"Members already present in DB ({existing}), skipping member seeding.")

        print("Seed finished.")
    except Exception as e:
        print("Seed failed:", e)
    finally:
        db.close()

if __name__ == "__main__":
    main()
