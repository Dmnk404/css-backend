from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth_utils import require_admin
from app.models.user import User  # Used for type hinting the authenticated admin user

# Dependency Imports
from app.routers.auth import get_current_user
from app.schemas.member import MemberCreate, MemberRead, MemberUpdate

# Service and Schema Imports
from app.services.member_service import MemberService, get_member_service

# --- Router Initialization ---
router = APIRouter(prefix="/members", tags=["Members"])


@router.get("/", response_model=List[MemberRead])
def read_members(
    name: Optional[str] = Query(None, description="Search by member name (substring)."),
    birth_date: Optional[date] = Query(
        None, description="Search by exact birth date (YYYY-MM-DD)."
    ),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of results to return."
    ),
    member_service: MemberService = Depends(get_member_service),
    # Authentication required for all users accessing the list
    user=Depends(get_current_user),
):
    """
    Retrieves all members or filters them based on optional query parameters.
    """
    # Delegation of logic to the Service Layer
    members = member_service.get_members(name=name, birth_date=birth_date, limit=limit)
    return members


@router.post("/", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
def create_member(
    member: MemberCreate,
    member_service: MemberService = Depends(get_member_service),
    # AUTHORIZATION: Only Admins can create a new member
    admin_user: User = Depends(require_admin),
):
    """
    Creates a new member (Admin only).
    """
    return member_service.create_member(member)


@router.put("/{member_id}", response_model=MemberRead)
def update_member(
    member_id: int,
    member_update: MemberUpdate,
    member_service: MemberService = Depends(get_member_service),
    # AUTHORIZATION: Only Admins can update a member
    admin_user: User = Depends(require_admin),
):
    """
    Updates an existing member by ID (Admin only).
    """
    # Check if member exists
    db_member = member_service.get_member_by_id(member_id)
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found"
        )

    # Update member via service
    return member_service.update_member(db_member, member_update)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    member_id: int,
    member_service: MemberService = Depends(get_member_service),
    # AUTHORIZATION: Only Admins can delete a member
    admin_user: User = Depends(require_admin),
):
    """
    Deletes a member by ID (Admin only).
    """
    # Check if member exists
    db_member = member_service.get_member_by_id(member_id)
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found"
        )

    # Delete member via service
    member_service.delete_member(db_member)
    return

    # End of file
