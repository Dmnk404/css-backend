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

Wichtiger Hinweis: In der Entwicklungs‑Docker‑Konfiguration wird uvicorn mit `--reload` gestartet. Für Produktion nicht verwenden.

Schnelle Demo‑Daten (optional)
------------------------------
- Falls ein Seed‑Script existiert (z. B. `app/scripts/seed.py`), kann das ausgeführt werden:
```bash
docker-compose exec app python app/scripts/seed.py
```
- Ansonsten kannst du die folgenden Requests benutzen, um schnell einen Testnutzer und einige Members anzulegen.

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
Beispielantwort:
```json
{"id":1,"username":"demo_user","email":"demo@example.com"}
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
Erwartete Minimalantwort (HTTP 201/200): JSON mit dem angelegten Member (id, Felder).

5) Alle Members listen (Pagination‑Beispiel)
```bash
curl -X GET "http://localhost:8000/members?limit=10&offset=0" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```
Antwort: Liste der Member‑Objekte im JSON‑Array.

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

Fehlerbehebung während Demo
---------------------------
- Falls ein Endpoint 500 liefert: Logs anschauen:
```bash
docker-compose logs -f app
```
- Falls Token als „invalid or expired“ abgelehnt wird: Zeit auf dem Demo‑Rechner prüfen / Token neulogin ausführen.

Weitere Hinweise
----------------
- OpenAPI JSON: http://localhost:8000/openapi.json (kann exportiert oder in Postman/Insomnia importiert werden)
- Tests lokal ausführen:
```bash
docker-compose exec app python -m pytest tests/
```