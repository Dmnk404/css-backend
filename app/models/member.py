from sqlalchemy import Column, Integer, String, Date, Boolean, Numeric, DateTime, func
from app.db.database import Base

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    birth_date = Column(Date, nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    postal_code = Column(String(20), nullable=False)
    phone = Column(String(50), nullable=True)

    join_date = Column(Date, server_default=func.current_date(), nullable=False)
    active = Column(Boolean, server_default="true", nullable=False)
    total_amount_received = Column(Numeric(10, 2), server_default="0.00", nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Member(id={self.id}, name={self.name}, email={self.email})>"
