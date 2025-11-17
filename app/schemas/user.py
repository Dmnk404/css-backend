from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

class UserRead(UserBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
