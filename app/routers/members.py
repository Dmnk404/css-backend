from fastapi import APIRouter
from app.models.member import Member

router = APIRouter(prefix="/members", tags=["Members"])

# Beispiel-Daten
members_db = [
    Member(id=1, name="Dominik", join_date="2024-01-15"),
    Member(id=2, name="Sven", join_date="2024-02-10", is_active=False)
]

@router.get("/", response_model=list[Member])
def get_all_members():
    return members_db

@router.get("/{member_id}", response_model=Member)
def get_member(member_id: int):
    for member in members_db:
        if member.id == member_id:
            return member
    return {"error": "Member not found"}
