from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reset_tokens = relationship("PasswordResetToken", back_populates="user")
    role_id = Column(
            Integer,
            ForeignKey("roles.id"),
            nullable=False,
            server_default="2",
            default=2
    )
    role = relationship("Role", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
