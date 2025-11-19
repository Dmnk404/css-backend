from typing import List, Optional, Type
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from fastapi import Depends  # NEU: Depends importieren

from app.db import get_db  # NEU: get_db importieren

from app.models.member import Member
from app.schemas.member import MemberCreate, MemberUpdate


class MemberService:
    """
    Kapselt die Geschäftslogik für die Mitgliederverwaltung (CRUD-Operationen und Filterung).
    """

    def __init__(self, db: Session):
        self.db = db

    def get_member_by_id(self, member_id: int) -> Optional[Member]:
        """Ruft ein Mitglied anhand der ID ab."""
        return self.db.query(Member).filter(Member.id == member_id).first()

    def get_members(
            self,
            name: Optional[str] = None,
            birth_date: Optional[date] = None,
            limit: int = 100
    ) -> List[Member]:
        """Ruft Mitglieder ab, mit optionaler Filterung."""
        query = self.db.query(Member)

        if name:
            # Fall-unabhängige Suche nach Teilstring
            query = query.filter(Member.name.ilike(f"%{name}%"))

        if birth_date:
            # Exakter Vergleich des Geburtsdatums
            query = query.filter(Member.birth_date == birth_date)

        return query.limit(limit).all()

    def create_member(self, member_data: MemberCreate) -> Member:
        """Erstellt ein neues Mitglied in der Datenbank."""

        # Erstelle ein Dict aus den Pydantic-Daten, aber nur wenn der Wert gesetzt ist
        member_dict = member_data.model_dump(exclude_none=True)

        db_member = Member(**member_dict)
        self.db.add(db_member)
        self.db.commit()
        self.db.refresh(db_member)
        return db_member

    def update_member(self, member: Member, update_data: MemberUpdate) -> Member:
        """Aktualisiert die Attribute eines bestehenden Mitglieds."""

        # Iteriere nur über die gesetzten (nicht None) Werte im Update-Schema
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(member, key, value)

        # SQLAlchemy setzt func.now() (onupdate) automatisch für updated_at
        self.db.commit()
        self.db.refresh(member)
        return member

    def delete_member(self, member: Member) -> None:
        """Löscht ein Mitglied."""
        self.db.delete(member)
        self.db.commit()


# Dependency, um den Service in den Routern zu injizieren
def get_member_service(db: Session = Depends(get_db)) -> MemberService:
    return MemberService(db)