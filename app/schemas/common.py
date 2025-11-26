from pydantic import BaseModel, EmailStr, Field


class PasswordResetRequest(BaseModel):
    """Schema for requesting a password reset via email."""

    email: EmailStr


class PasswordReset(BaseModel):
    """Scheme for entering the reset token and the new password."""

    token: str = Field(..., description="The plaintext reset token from the email.")
    new_password: str = Field(
        ...,
        min_length=8,
        description="The user's new password (at least 8 characters).",
    )
