from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.db import get_db
from app.models.member import Member
from app.schemas import MemberCreate, MemberRead, MemberUpdate
from app.routers.auth import get_current_user  # JWT-Dependency für Schutz der Endpoints

router = APIRouter(prefix="/members", tags=["Members"])


@router.get("/", response_model=List[MemberRead])
def read_members(
        name: str | None = Query(None, description="Suche nach Mitgliedsnamen (Teilstring)."),
        birth_date: date | None = Query(None, description="Suche nach exaktem Geburtsdatum (YYYY-MM-DD)."),
        limit: int = Query(100, ge=1, le=1000, description="Maximale Anzahl der zurückgegebenen Ergebnisse."),

        # Dependencies
        db: Session = Depends(get_db),
        user=Depends(get_current_user)
):
    """
    Ruft alle Mitglieder ab oder filtert sie basierend auf optionalen Query-Parametern.
    """
    query = db.query(Member)

    # Filter 1: Suche nach Name (fall-unabhängige LIKE-Suche)
    if name:
        # Angenommen, dein Member-Modell hat ein Feld 'name'
        query = query.filter(Member.name.ilike(f"%{name}%"))

    # Filter 2: Suche nach Geburtsdatum
    if birth_date:
        # Vergleiche das Geburtsdatum exakt
        query = query.filter(Member.birth_date == birth_date)

        # Weitere Filter (z.B. nach E-Mail, Status etc.) können hier hinzugefügt werden

    # Pagination/Limit
    members = query.limit(limit).all()

    return members

@router.post("/", response_model=MemberRead)
def create_member(member: MemberCreate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    new_member = Member(**member.model_dump())
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

@router.put("/{member_id}", response_model=MemberRead)
def update_member(member_id: int, member: MemberUpdate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    db_member = db.query(Member).filter(Member.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    for key, value in member.model_dump(exclude_unset=True).items():
        setattr(db_member, key, value)
    db.commit()
    db.refresh(db_member)
    return db_member

@router.delete("/{member_id}")
def delete_member(member_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    db_member = db.query(Member).filter(Member.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(db_member)
    db.commit()
    return {"detail": "Member deleted"}
