from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class MemberBase(BaseModel):
    name: str
    email: EmailStr
    address: Optional[str] = None
    birth_date: Optional[date] = None
    total_amount_received: Optional[float] = 0.0

class MemberCreate(MemberBase):
    pass

class MemberRead(MemberBase):
    id: int

    class Config:
        from_attributes = True
