import pytest

from app.schemas.member import MemberCreate, MemberUpdate
from app.services.member_service import MemberService


def sample_member_payload(index: int = 0) -> dict:
    """Vollständiges Member-Objekt mit dem einzigen Namensfeld `name`."""
    return {
        "name": f"Test Member {index}",
        "birth_date": "1990-01-01",  # ISO-Format
        "address": f"Street {index} 1",
        "city": "Berlin",
        "postal_code": "10115",
        "email": f"t{index}@example.com",
    }


def test_create_get_update_delete_member(db_session):
    svc = MemberService(db_session)
    payload = MemberCreate(**sample_member_payload(1))
    member = svc.create_member(payload)
    assert member.id is not None
    assert member.email == "t1@example.com"

    fetched = svc.get_member_by_id(member.id)
    assert fetched.id == member.id

    # Update nur des `name`-Feldes
    update_payload = MemberUpdate(name="Updated Name")
    updated = svc.update_member(member, update_payload)
    assert updated.name == "Updated Name"

    svc.delete_member(member)
    assert svc.get_member_by_id(member.id) is None


def test_create_member_duplicate_email_raises(db_session):
    svc = MemberService(db_session)
    svc.create_member(MemberCreate(**sample_member_payload(2)))
    with pytest.raises(Exception):
        svc.create_member(MemberCreate(**sample_member_payload(2)))
