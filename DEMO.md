```markdown
# Kurze Demo-Anleitung (DEMO.md)

Zweck
-----
Diese Datei zeigt in wenigen Schritten, wie du die Kern‑Flows der API demonstrierst:
- Benutzer registrieren / einloggen (JWT)
- Mitglieder anlegen / abrufen (geschützter CRUD‑Flow)
- Nutzung der automatisch generierten API‑Docs (/docs)

Wichtiger Hinweis vor der Registrierung
--------------------------------------
Die Registrierung legt neue Nutzer an, erwartet aber in der Datenbank eine Standard‑Rolle mit dem Namen "Member". Falls diese Rolle nicht vorhanden ist, schlägt die Registrierung mit einem Fehler (HTTP 500, "Default role not found") fehl.

Am einfachsten legst du die Rolle per Seed‑Script an (empfohlen):
```bash
# führt das Seed-Script aus, welches Role 'Member', einen admin user und Demo-Members erstellt
docker-compose exec app python app/scripts/seed.py
```

Quickstart (lokal per Docker)
-----------------------------
1. Repository klonen und in das Verzeichnis wechseln:
```bash
git clone https://github.com/Dmnk404/css-backend.git
cd css-backend
```

2. Container bauen und starten:
```bash
docker-compose up -d --build
```

3. Datenbank migrations ausführen (einmalig nach Start):
```bash
docker-compose exec app alembic upgrade head
```

4. API im Browser öffnen:
- Swagger / OpenAPI UI: http://localhost:8000/docs
- Root / health: http://localhost:8000/

Schnelle Demo‑Daten (optional)
------------------------------
- Seed script (legt Role 'Member', admin user und Beispiel‑Members an):
```bash
docker-compose exec app python app/scripts/seed.py
```

Demo‑Flows (curl‑Beispiele)
--------------------------
Hinweis: Die Auth‑Endpoints sind unter `/auth` (siehe `app/routers/auth.py`).

1) Benutzer registrieren
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "email": "demo@example.com",
    "password": "demo_pass"
  }'
```
Erwartete Minimal‑Antwort (HTTP 201):
```json
{"message": "User 'demo_user' successfully registered."}
```

2) Benutzer einloggen (OAuth2 Password form)
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo_user&password=demo_pass"
```
Erwartete Antwort:
```json
{"access_token":"<JWT_TOKEN>","token_type":"bearer"}
```
Merke dir das `<JWT_TOKEN>` für geschützte Requests.

3) Aktuellen User abrufen (geschützt)
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

4) Member anlegen (geschützt)
```bash
curl -X POST http://localhost:8000/members \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "first_name": "Max",
    "last_name": "Mustermann",
    "email": "max@example.com",
    "notes": "Demo-Mitglied"
  }'
```

5) Alle Members listen (Pagination‑Beispiel)
```bash
curl -X GET "http://localhost:8000/members?limit=10&offset=0" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

6) Einzelnes Member abrufen
```bash
curl -X GET http://localhost:8000/members/1 \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

Tipps für die Präsentation
--------------------------
- Öffne zuerst `/docs` im Browser: dort sieht man das API‑Surface, die Schemas und kann Requests interaktiv ausführen.
- Zeige kurz die Registrierung → Login → Ausgabe des JWT → Verwendung des JWT für einen geschützten POST/GET.
- Falls die Demo live gezeigt wird, lade vorher Seed‑Daten, damit die Listen gefüllt sind.
- Erwähne in der Präsentation: Datenbank ist PostgreSQL (in Docker Compose), Migrationen per Alembic, Auth per JWT (security in `app/core/security.py`), Validierung per Pydantic‑Schemas.
```
