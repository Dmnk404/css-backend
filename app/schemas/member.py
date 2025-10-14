from pydantic import BaseModel
from datetime import date
from typing import Optional

class MemberBase(BaseModel):
    name: str
    email: str
    birth_date: date
    address: str
    city: str
    postal_code: str
    phone: Optional[str] = None
    join_date: Optional[date] = None
    active: Optional[bool] = True
    total_amount_received: Optional[float] = 0.0

class MemberCreate(MemberBase):
    pass  # alles erforderlich beim Erstellen

class MemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
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

    class Config:
        from_attributes = True  # Pydantic v2: früher orm_mode = True
