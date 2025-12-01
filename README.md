# CSC-Backend: Mitglieder- und Dokumentationsverwaltung

Ein FastAPI-Backend für die Verwaltung von Mitgliedsdaten und rechtlich relevanten Produktionsdokumentationen für Cannabis Social Clubs.

## 🌐 Live Demo

**🚀 Die API ist live deployed auf Render:**

- **Live URL:** https://css-backend-tsum.onrender.com
- **API Dokumentation (Swagger UI):** https://css-backend-tsum.onrender.com/docs
- **Alternative Dokumentation (ReDoc):** https://css-backend-tsum.onrender.com/redoc

### 🔐 Test Credentials

- **Admin User:** `admin` / `adminpass`
- **Demo-Daten:** 3 Beispiel-Mitglieder sind bereits vorgeladen

### 📊 API Features

- ✅ REST API mit FastAPI
- ✅ PostgreSQL Datenbank
- ✅ JWT Authentication (Bearer Token)
- ✅ 4 Entities: User, Role, Member, PasswordResetToken
- ✅ Pydantic Validation & Schemas
- ✅ Automatische API-Dokumentation
- ✅ Role-based Access Control (Admin/Member)
- ✅ Password Reset Flow
- ✅ CORS-ready für Frontend-Integration

---

## 🚀 Technologie-Stack

* **Framework:** Python 3.12+ / FastAPI 0.109.0
* **Datenbank:** PostgreSQL 16
* **ORM/Migration:** SQLAlchemy 2.0 / Alembic 1. 13
* **Authentication:** JWT (python-jose) + PBKDF2 Password Hashing
* **Validation:** Pydantic 2. 5
* **Deployment:** Render. com (Web Service + PostgreSQL)
* **Containerisierung:** Docker / Docker Compose (lokale Entwicklung)
* **Testing:** Pytest mit SQLite in-memory DB

---

## 📁 Projektstruktur

```
css-backend/
├── app/
│   ├── core/              # Core-Funktionalität (Config, Security)
│   │   ├── config.py      # Pydantic Settings
│   │   └── security.py    # JWT & Password Hashing
│   ├── models/            # SQLAlchemy Models
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── member.py
│   │   └── password_reset_token.py
│   ├── routers/           # FastAPI Routers (Endpoints)
│   │   ├── auth.py        # Login, Register, Password Reset
│   │   ├── members.py     # CRUD für Members
│   │   └── password_reset.py
│   ├── schemas/           # Pydantic Schemas (Request/Response)
│   ├── scripts/           # Utility Scripts
│   │   └── seed. py        # Demo-Daten laden
│   ├── db. py              # Database Session & Base
│   └── main.py            # FastAPI App Entry Point
├── alembic/               # Database Migrations
├── tests/                 # Pytest Tests
├── docker-compose.yml     # Lokale Entwicklungsumgebung
├── Dockerfile             # Production Image
├── render.yaml            # Render Deployment Config
├── requirements.txt       # Python Dependencies
└── . env. example           # Template für Environment Variables
```

---

## 🛠️ Lokale Entwicklung

### Voraussetzungen

- **Docker** & **Docker Compose** installiert
- **Git** installiert

### Setup

1.  **Projekt klonen:**
    ```bash
    git clone https://github.com/Dmnk404/css-backend.git
    cd css-backend
    ```

2.  **Environment Variables einrichten:**
    ```bash
    cp .env.example .env
    ```

    Bearbeite `. env` und passe die Werte an (für lokale Entwicklung sind die Defaults meist OK).

3.  **Container starten:**
    ```bash
    docker-compose up -d --build
    ```

    Das startet:
    - **app** (FastAPI auf Port 8000)
    - **db** (PostgreSQL auf Port 5432)

4.  **Datenbank initialisieren:**
    ```bash
    # Migrationen ausführen (Tabellen erstellen)
    docker-compose exec app alembic upgrade head

    # Demo-Daten laden (Admin + 3 Members)
    docker-compose exec app python app/scripts/seed.py
    ```

5.  **API aufrufen:**
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
    - Health Check: http://localhost:8000/

---

## 🧪 Tests ausführen

Die Tests verwenden eine **SQLite in-memory Datenbank**, um die PostgreSQL-DB nicht zu beeinflussen.

```bash
# Alle Tests ausführen
docker-compose exec app python -m pytest tests/

# Tests mit Coverage
docker-compose exec app python -m pytest tests/ --cov=app --cov-report=term-missing

# Einzelne Test-Datei
docker-compose exec app python -m pytest tests/test_auth.py -v
```

**Erwartetes Ergebnis:** Alle Tests sollten grün sein ✅

---

## 📡 API Endpoints

### 🔐 Authentication (`/auth`)

| Method | Endpoint | Beschreibung | Auth |
|--------|----------|--------------|------|
| POST | `/auth/register` | Neuen User registrieren | ❌ |
| POST | `/auth/login` | Login (JWT Token erhalten) | ❌ |
| GET | `/auth/me` | Aktuellen User abrufen | ✅ |
| POST | `/auth/request-password-reset` | Password Reset anfragen | ❌ |
| POST | `/auth/reset-password` | Passwort mit Token zurücksetzen | ❌ |

### 👥 Members (`/members`)

| Method | Endpoint | Beschreibung | Auth | Role |
|--------|----------|--------------|------|------|
| GET | `/members` | Alle Members auflisten | ✅ | Admin/Member |
| POST | `/members` | Neuen Member erstellen | ✅ | Admin |
| GET | `/members/{id}` | Einzelnen Member abrufen | ✅ | Admin/Member |
| PUT | `/members/{id}` | Member aktualisieren | ✅ | Admin |
| DELETE | `/members/{id}` | Member löschen | ✅ | Admin |

**Auth:** ✅ = JWT Bearer Token erforderlich

---

## 🔑 Environment Variables

Folgende Variablen müssen gesetzt werden (siehe `.env.example`):

| Variable | Beschreibung | Beispiel |
|----------|--------------|----------|
| `DATABASE_URL` | PostgreSQL Connection String | `postgresql://user:pass@localhost:5432/db` |
| `SECRET_KEY` | JWT Secret (min.  32 Zeichen) | `your-super-secret-key-here-min-32-chars` |
| `ALGORITHM` | JWT Algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token-Gültigkeit in Minuten | `1440` (24h) |
| `ENVIRONMENT` | Environment (development/production) | `development` |

---

## 🚀 Deployment auf Render

Das Projekt ist bereits auf [Render.com](https://render.com) deployed.

### Automatisches Deployment

Bei jedem `git push` zu `main`:
1. Render baut das Docker Image neu
2. Führt automatisch Migrationen aus
3. Lädt Seed-Daten (falls DB leer)
4. Startet die App

### Manuelles Deployment

1. **Render Account erstellen** und mit GitHub verbinden
2. **New Web Service** erstellen
3. **Repository** `Dmnk404/css-backend` auswählen
4. **PostgreSQL Database** erstellen (`css-db`)
5. **Environment Variables** setzen:
   - `DATABASE_URL` → From Database: `css-db`
   - `SECRET_KEY` → Generate oder manuell setzen
   - `ENVIRONMENT` → `production`
6. **Deploy** starten

Die `render.yaml` definiert alle Einstellungen automatisch.

---

## 🎯 Demo-Flow für Präsentation

### 1. API Dokumentation öffnen
```
https://css-backend-tsum.onrender.com/docs
```

### 2. Als Admin einloggen
**POST `/auth/login`**
```json
{
  "username": "admin",
  "password": "adminpass"
}
```
→ Token kopieren

### 3. Autorisieren
- Klicke auf **"Authorize"** 🔒
- Füge ein: `Bearer <dein-token>`
- Klicke **"Authorize"**

### 4. Members abrufen
**GET `/members`**
→ Zeigt 3 Demo-Members

### 5. Neuen Member erstellen
**POST `/members`** (nur als Admin!)
```json
{
  "name": "Test User",
  "email": "test@example.com",
  "birth_date": "1995-01-01",
  "address": "Teststraße 1",
  "city": "Berlin",
  "postal_code": "10115",
  "phone": "030-12345678"
}
```

---

## 🔄 Datenbank-Migrationen

### Neue Migration erstellen
```bash
docker-compose exec app alembic revision --autogenerate -m "Beschreibung"
```

### Migration ausführen
```bash
docker-compose exec app alembic upgrade head
```

### Migration rückgängig machen
```bash
docker-compose exec app alembic downgrade -1
```

### Aktuellen Stand anzeigen
```bash
docker-compose exec app alembic current
```

---

## 📝 Weitere Skripte

### Seed-Daten neu laden
```bash
docker-compose exec app python app/scripts/seed.py
```

### Logs anzeigen
```bash
# Alle Services
docker-compose logs -f

# Nur App
docker-compose logs -f app

# Nur Database
docker-compose logs -f db
```

### Container neu starten
```bash
docker-compose restart app
```

### Alles stoppen und aufräumen
```bash
docker-compose down -v
```

---

## 🐛 Troubleshooting

### Problem: "relation does not exist"
**Lösung:** Migrationen ausführen
```bash
docker-compose exec app alembic upgrade head
```

### Problem: "SECRET_KEY is missing"
**Lösung:** `. env` Datei prüfen und `SECRET_KEY` setzen

### Problem: Database Connection refused
**Lösung:**
```bash
# Container neu starten
docker-compose down
docker-compose up -d

# Logs prüfen
docker-compose logs db
```

### Problem: Tests schlagen fehl
**Lösung:**
```bash
# Test-Dependencies installieren
docker-compose exec app pip install -r requirements.txt

# Cache löschen
docker-compose exec app pytest --cache-clear
```

---

## 📚 Weitere Ressourcen

- [FastAPI Dokumentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Dokumentation](https://docs.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Pydantic Dokumentation](https://docs.pydantic.dev/)
- [JWT. io](https://jwt.io/) - JWT Debugger

---

## 📄 Lizenz

Dieses Projekt ist für Bildungszwecke entwickelt worden.

---

## 👤 Autor

**Dominik** - [GitHub](https://github.com/Dmnk404)

---

## 🎯 MVP Requirements ✅

- ✅ REST API (FastAPI)
- ✅ PostgreSQL Database mit 4 Entities
- ✅ Mehrere Endpoints pro Entity
- ✅ JWT Authentication
- ✅ Pydantic Validation
- ✅ Deployed auf Render mit ENV Variables
- ✅ GitHub Dokumentation
- ✅ Keine UI (nur API)
- ✅ Automatische Migrationen
- ✅ Demo-Daten vorgeladen
