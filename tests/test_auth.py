import pytest
import httpx


def test_register_user_success(client):
    """Testet die erfolgreiche Registrierung eines neuen Benutzers."""
    user_data = {
        "username": "unique_success_user",  # <-- NEU: Eindeutiger Name
        "password": "securepassword123"
    }
    response = client.post("/auth/register", json=user_data)

    # Hier erwarten wir 201 Created
    assert response.status_code == 201
    assert "erfolgreich registriert" in response.json().get("message")


def test_register_user_duplicate(client):
    """Testet die Registrierung eines Benutzers, der bereits existiert."""

    # Stellen Sie sicher, dass dieser Test einen anderen Namen verwendet,
    # der noch nicht im Erfolgs-Test verwendet wurde.
    unique_name = "unique_duplicate_user"
    user_data = {
        "username": unique_name,
        "password": "securepassword123"
    }

    # 1. Registriere den Benutzer zuerst erfolgreich
    client.post("/auth/register", json=user_data)  # Code 201

    # 2. Versuche, ihn erneut zu registrieren
    response = client.post("/auth/register", json=user_data)

    # Prüfe den Fehlerstatuscode
    assert response.status_code == 400
    assert "Benutzername ist bereits vergeben" in response.json().get("detail")


@pytest.mark.parametrize("username, password, expected_status", [
    ("testuser_login", "correctpw", 200),
    ("testuser_login", "wrongpw", 401),
    ("nonexistent", "anypw", 401),
])
def test_login_and_token_creation(client, username, password, expected_status):
    """Testet Login und JWT-Token-Generierung."""

    # 1. Sicherstellen, dass der Benutzer existiert (nur für den Erfolgsfall)
    if expected_status == 201:
        client.post("/auth/register", json={"username": username, "password": password})

    # 2. Login-Anfrage senden (Formular-Daten!)
    login_data = {
        "username": username,
        "password": password,
        "grant_type": "password",  # Nötig für OAuth2PasswordRequestForm
        "scope": ""
    }

    response = client.post("/auth/login", data=login_data)

    assert response.status_code == expected_status

    if expected_status == 201:
        # Prüfe, ob das Token im richtigen Format zurückkommt
        assert "access_token" in response.json()
        assert response.json().get("token_type") == "bearer"