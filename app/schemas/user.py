from pydantic import BaseModel, constr

class UserCreate(BaseModel):
    username: str
    password: constr(min_length=6, max_length=12)

class UserRead(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
