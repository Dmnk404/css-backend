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

from app.core.security import get_password_hash
from app.db import SessionLocal
from app.models.member import Member
from app.models.role import Role
from app.models.user import User

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
        "email": "ada@demo. org",
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
        # WICHTIG: Erstelle BEIDE Rollen
        member_role = db.query(Role).filter(Role.name == "Member").first()
        if not member_role:
            member_role = Role(name="Member")
            db.add(member_role)
            db.commit()
            db.refresh(member_role)
            print("Created Role 'Member'")

        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            admin_role = Role(name="Admin")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("Created Role 'Admin'")

        # Admin user mit Admin-Rolle!
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("adminpass"),
                role=admin_role,  # <- GEÄNDERT: Admin-Rolle!
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("Created admin user (username=admin, password=adminpass) with Admin role")
        elif admin.role.name != "Admin":
            # Falls Admin bereits existiert aber falsche Rolle hat
            admin.role = admin_role
            db.commit()
            print("Updated admin user to Admin role")

        # Seed Members
        existing_count = db.query(Member).count()
        if existing_count == 0:
            for m in EXAMPLE_MEMBERS:
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