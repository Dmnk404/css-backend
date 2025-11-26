from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class MemberBase(BaseModel):
    name: str
    email: EmailStr
    birth_date: date
    address: str
    city: str
    postal_code: str
    phone: Optional[str] = None


class MemberCreate(MemberBase):
    join_date: Optional[date] = None  # optional, DB-Default greift sonst
    active: Optional[bool] = None
    total_amount_received: Optional[float] = None


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    birth_date: Optional[date] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    join_date: Optional[date] = None
    active: Optional[bool] = None
    total_amount_received: Optional[float] = None


class MemberRead(MemberBase):
    id: int
    join_date: date
    active: bool
    total_amount_received: float

    model_config = ConfigDict(from_attributes=True)
