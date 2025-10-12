from pydantic import BaseModel

class MemberBase(BaseModel):
    name: str
    email: str

class MemberCreate(MemberBase):
    pass

class MemberRead(MemberBase):
    id: int

    class Config:
        orm_mode = True
