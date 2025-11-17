import pytest

# -------------------------------
# 🔹 Registrierungstests
# -------------------------------
def test_register_user_success(client):
    """Testet die erfolgreiche Registrierung eines neuen Benutzers."""
    user_data = {
        "username": "unique_success_user",
        "email": "unique_success_user@example.com",
        "password": "securepassword123"
    }

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 201
    assert "successfully registered" in response.json().get("message", "")


def test_register_user_duplicate(client):
    """Testet die Registrierung eines Benutzers, der bereits existiert."""
    user_data = {
        "username": "duplicate_user",
        "email": "duplicate_user@example.com",
        "password": "securepassword123"
    }

    # 1️⃣ Benutzer erfolgreich registrieren
    first = client.post("/auth/register", json=user_data)
    assert first.status_code == 201

    # 2️⃣ Versuch, denselben Benutzer erneut zu registrieren
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Username is already taken" in response.json().get("detail", "")


# -------------------------------
# 🔹 Login-Tests
# -------------------------------
@pytest.mark.parametrize(
    "username,password,expected_status,expect_token",
    [
        ("testuser_login_success", "correctpw", 200, True),   # ✅ Erfolgreicher Login
        ("testuser_login_fail", "wrongpw", 401, False),       # ❌ Falsches Passwort
        ("nonexistent_user", "anypw", 401, False),            # ❌ Unbekannter Benutzer
    ],
)
def test_login_and_token_creation(client, username, password, expected_status, expect_token):
    """Testet Login und JWT-Token-Generierung unter verschiedenen Bedingungen."""

    # 1️⃣ Benutzer anlegen (nur für Erfolgsfall)
    if expect_token:
        register_payload = {
            "username": username,
            "email": f"{username}@example.com",
            "password": password
        }
        r = client.post("/auth/register", json=register_payload)
        assert r.status_code == 201, f"Registrierung für Testuser {username} fehlgeschlagen: {r.text}"

    # 2️⃣ Login-Anfrage senden (Form-encoded!)
    login_data = {
        "username": username,
        "password": password,
        "grant_type": "password",
    }

    response = client.post("/auth/login", data=login_data)
    assert response.status_code == expected_status

    if expect_token:
        data = response.json()
        assert "access_token" in data
        assert data.get("token_type") == "bearer"
    else:
        assert "access_token" not in response.text
