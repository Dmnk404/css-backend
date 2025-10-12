from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import SessionLocal
from app.models.member import Member
from app.schemas.member import MemberCreate, MemberRead

router = APIRouter(prefix="/members", tags=["Members"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Alle Mitglieder
@router.get("/", response_model=List[MemberRead])
def get_members(db: Session = Depends(get_db)):
    return db.query(Member).all()

# Einzelnes Mitglied
@router.get("/{member_id}", response_model=MemberRead)
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member

# Neues Mitglied
@router.post("/", response_model=MemberRead)
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    db_member = Member(name=member.name, email=member.email)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member
