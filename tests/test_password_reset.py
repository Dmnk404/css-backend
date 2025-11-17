import pytest
from datetime import datetime, timedelta, UTC
from app.core.security import generate_reset_token, hash_reset_token, verify_reset_token
from app.models import PasswordResetToken, User


def test_generate_and_verify_reset_token(db_session):
    """Ensure reset token generation, hashing, and verification works correctly."""
    token = generate_reset_token()
    hashed = hash_reset_token(token)

    assert len(token) > 20
    assert len(hashed) == 64  # SHA256 hexdigest length
    assert verify_reset_token(token, hashed)
    assert not verify_reset_token("wrongtoken", hashed)


def test_create_password_reset_entry(db_session):
    """Ensure that a password reset token can be saved and queried."""
    user = User(username="testuser", email="test@example.com", hashed_password="hashedpw")
    db_session.add(user)
    db_session.commit()

    plain_token = generate_reset_token()
    hashed_token = hash_reset_token(plain_token)
    expires = datetime.now(UTC) + timedelta(minutes=15)

    reset_token = PasswordResetToken(
        hashed_token=hashed_token,
        user_id=user.id,
        expires_at=expires
    )

    db_session.add(reset_token)
    db_session.commit()

    saved_token = db_session.query(PasswordResetToken).filter_by(user_id=user.id).first()
    assert saved_token is not None
    assert verify_reset_token(plain_token, saved_token.hashed_token)

def test_password_reset_flow(client, db_session):
    """Simulate a full password reset request and confirmation."""
    # 1. Create test user
    user = User(username="flowuser", email="flow@example.com", hashed_password="hashedpw")
    db_session.add(user)
    db_session.commit()

    # 2. Request password reset
    response = client.post("/auth/forgot-password", json={"email": "flow@example.com"})
    assert response.status_code == 200

    # 3. Get token from DB (simulating email link)
    db_token = db_session.query(PasswordResetToken).filter_by(user_id=user.id).first()
    assert db_token is not None

    # 4. Reset password
    # request reset token
    response = client.post("/auth/forgot-password", json={"email": "flow@example.com"})
    assert response.status_code == 200

    # TESTMODE: The real token is returned
    token = response.json()["test_token"]

    reset_data = {
        "token": token,
        "new_password": "newsecret123"
    }
    response = client.post("/auth/reset-password", json=reset_data)
    assert response.status_code == 200

    assert response.status_code in (200, 204)
