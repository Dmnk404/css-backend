# 🎤 Präsentations-Guide: CSS-Backend MVP

## 📋 Präsentations-Flow (5-10 Minuten)

### 1.  Intro (1 Min)
- **Projekt:** Backend für Cannabis Social Clubs in Deutschland
- **Zweck:** Mitgliederverwaltung, Produktion & Distribution
- **Tech:** FastAPI, PostgreSQL, JWT Auth

### 2. Live Demo - API Dokumentation (2 Min)

**Öffne:** https://css-backend-tsum.onrender.com/docs

**Zeige:**
- ✅ Automatische Swagger UI
- ✅ Alle Endpoints sichtbar
- ✅ Schemas/Models dokumentiert

### 3. Authentication Flow (2 Min)

**Demo:**
1. POST `/auth/login` mit `admin` / `adminpass`
2. Token kopieren
3. "Authorize" klicken → Token eingeben
4. GET `/auth/me` → Zeigt aktuellen User

**Erkläre:** JWT-basierte Authentifizierung, Bearer Token

### 4.  CRUD Operations (2 Min)

**Demo:**
1. GET `/members` → Liste 3 Demo-Members
2. POST `/members` → Erstelle neuen Member (nur als Admin!)
3. GET `/members/{id}` → Zeige einzelnen Member
4. PUT `/members/{id}` → Update Member

**Erkläre:** Role-based Access Control (Admin vs.  Member)

### 5.  Technische Details (2 Min)

**Zeige GitHub Repo:**
- ✅ Saubere Code-Struktur (`app/`, `routers/`, `models/`)
- ✅ Alembic Migrations
- ✅ Pydantic Schemas für Validation
- ✅ Tests vorhanden (`tests/`)
- ✅ Docker Setup für lokale Entwicklung
- ✅ `render.yaml` für Production Deployment

### 6. Deployment (1 Min)

**Zeige Render Dashboard:**
- ✅ Auto-Deploy bei Git Push
- ✅ Environment Variables gesetzt
- ✅ PostgreSQL Database verbunden
- ✅ Logs einsehbar

---

## 🎯 MVP Requirements - Alle erfüllt!

- ✅ REST API (FastAPI)
- ✅ PostgreSQL mit 4 Entities
- ✅ Mehrere Endpoints pro Entity
- ✅ JWT Authentication
- ✅ Pydantic Validation
- ✅ Deployed auf Render mit ENV Vars
- ✅ GitHub Dokumentation
- ✅ Keine UI (nur API)

---

## 💡 Mögliche Fragen & Antworten

**Q: Warum FastAPI?**
A: Schnell, moderne Python-Features, automatische API-Docs, async support

**Q: Wie funktioniert die Authentication?**
A: JWT Tokens mit Bearer Auth, Passwort-Hashing mit PBKDF2

**Q: Wie deployed?**
A: Render. com mit automatischem Build bei Git Push, PostgreSQL managed database

**Q: Tests?**
A: Pytest mit SQLite in-memory DB für isolierte Tests

**Q: Nächste Schritte?**
A: Frontend (React/Vue), erweiterte Berechtigungen, Logging, Monitoring
