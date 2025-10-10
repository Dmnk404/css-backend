from pydantic import BaseModel
from typing import Optional

class Member(BaseModel):
    id: int
    name: str
    join_date: Optional[str] = None
    is_active: bool = True
