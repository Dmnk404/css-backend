from datetime import UTC, datetime, timedelta

from app.core.security import generate_reset_token, hash_reset_token, verify_reset_token
from app.models import PasswordResetToken, Role, User


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
    # ✅ User mit role_id erstellen
    role = db_session.query(Role).filter(Role.name == "User").first()
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpw",
        role_id=role.id,
    )
    db_session.add(user)
    db_session.commit()

    plain_token = generate_reset_token()
    hashed_token = hash_reset_token(plain_token)
    expires = datetime.now(UTC) + timedelta(minutes=15)

    reset_token = PasswordResetToken(
        hashed_token=hashed_token, user_id=user.id, expires_at=expires
    )

    db_session.add(reset_token)
    db_session.commit()

    saved_token = (
        db_session.query(PasswordResetToken).filter_by(user_id=user.id).first()
    )
    assert saved_token is not None
    assert verify_reset_token(plain_token, saved_token.hashed_token)


def test_password_reset_flow(client, db_session, monkeypatch):
    """Simulate a full password reset request and confirmation."""

    # ✅ TESTING=1 setzen für test_token Rückgabe
    monkeypatch.setenv("TESTING", "1")

    # ✅ 1. Create test user mit role_id
    role = db_session.query(Role).filter(Role.name == "User").first()
    user = User(
        username="flowuser",
        email="flow@example.com",
        hashed_password="hashedpw",
        role_id=role.id,
    )
    db_session.add(user)
    db_session.commit()

    # 2. Request password reset
    response = client.post(
        "/auth/password-reset-request", json={"email": "flow@example.com"}
    )
    assert response.status_code == 200

    # ✅ TESTMODE: The real token is returned
    response_data = response.json()
    assert (
        "test_token" in response_data
    ), f"Expected 'test_token' in response, got: {response_data}"
    token = response_data["test_token"]

    # 3. Get token from DB (simulating email link) - zur Validierung
    db_token = db_session.query(PasswordResetToken).filter_by(user_id=user.id).first()
    assert db_token is not None

    # 4. Reset password with the token
    reset_data = {"token": token, "new_password": "newsecret123"}
    response = client.post("/auth/reset-password", json=reset_data)
    assert response.status_code == 200

    response_data = response.json()
    assert "message" in response_data
    assert "flowuser" in response_data["message"]
