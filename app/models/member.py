from datetime import date
from sqlalchemy import Column, Integer, String, Date, Boolean, Float
from app.db import Base

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    birth_date = Column(Date, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    phone = Column(String, nullable=True)

    join_date = Column(Date, nullable=False, default=date.today)
    active = Column(Boolean, default=True)
    total_amount_received = Column(Float, default=0.0)