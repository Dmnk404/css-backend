#!/usr/bin/env python3
"""
Seed script for css-backend.

- Creates Role 'Member' if it doesn't exist
- Creates an admin/test user (username: admin / password: adminpass) if not present
- Creates a few example Members, filling all NOT NULL fields
Usage:
  # inside container:
  python app/scripts/seed.py

Make sure to run migrations first:
  docker-compose exec app alembic upgrade head
"""
from datetime import date
from app.db import SessionLocal
from app.core.security import get_password_hash

# Import models (adjust if your repo exports differently)
from app.models.role import Role
from app.models.user import User
from app.models.member import Member

EXAMPLE_MEMBERS = [
    {
        "name": "Max Mustermann",
        "email": "max@example.com",
        "birth_date": date(1990, 1, 1),
        "address": "Musterstraße 1",
        "city": "Musterstadt",
        "postal_code": "12345",
        "phone": "0123-456789",
    },
    {
        "name": "Erika Mustermann",
        "email": "erika@example.com",
        "birth_date": date(1985, 5, 12),
        "address": "Beispielweg 2",
        "city": "Beispielstadt",
        "postal_code": "23456",
        "phone": "0123-987654",
    },
    {
        "name": "Ada Lovelace",
        "email": "ada@demo.org",
        "birth_date": date(1992, 12, 10),
        "address": "Algorithmus Allee 3",
        "city": "Codecity",
        "postal_code": "34567",
        "phone": "030-1234567",
    },
]

def main():
    db = SessionLocal()
    try:
        # Role 'Member'
        role = db.query(Role).filter(Role.name == "Member").first()
        if not role:
            role = Role(name="Member")
            db.add(role)
            db.commit()
            db.refresh(role)
            print("Created Role 'Member'")

        # Admin user
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

        # Seed Members only if none exist (to avoid duplicates)
        existing_count = db.query(Member).count()
        if existing_count == 0:
            for m in EXAMPLE_MEMBERS:
                # double-check unique email
                if db.query(Member).filter(Member.email == m["email"]).first():
                    continue
                member = Member(
                    name=m["name"],
                    email=m["email"],
                    birth_date=m["birth_date"],
                    address=m["address"],
                    city=m["city"],
                    postal_code=m["postal_code"],
                    phone=m.get("phone"),
                    # join_date, active, total_amount_received, created_at use DB defaults
                )
                db.add(member)
            db.commit()
            print(f"Seeded {len(EXAMPLE_MEMBERS)} example members")
        else:
            print(f"{existing_count} members already present, skipping member seeding.")
        print("Seed finished.")
    except Exception as e:
        print("Seed failed:", e)
    finally:
        db.close()

if __name__ == "__main__":
    main()