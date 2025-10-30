from pydantic import BaseModel, constr
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: constr(min_length=6, max_length=128)

class UserRead(UserBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True

