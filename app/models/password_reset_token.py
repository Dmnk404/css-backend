from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base

class PasswordResetToken(Base):
    """
    Stores a hashed password reset token for a user.

    Fields
    - id: primary key
    - hashed_token: deterministic hash of the token sent to the user (e.g. SHA256 hex)
    - user_id: FK to users.id
    - expires_at: timezone-aware expiration timestamp
    - user: relationship back to User
    """
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    hashed_token = Column(String(128), index=True, nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # relationship to User; User must define `reset_tokens = relationship(..., back_populates="user")`
    user = relationship("User", back_populates="reset_tokens")
