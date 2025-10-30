# CSC-Backend: Mitglieder- und Dokumentationsverwaltung

Ein FastAPI-Backend für die Verwaltung von Mitgliedsdaten und rechtlich relevanten Produktionsdokumentationen.

## 🚀 Technologie-Stack

* **Framework:** Python 3.12+ / FastAPI
* **Datenbank:** PostgreSQL
* **ORM/Migration:** SQLAlchemy / Alembic
* **Containerisierung:** Docker / Docker Compose

## 🛠️ Entwicklungsumgebung starten (Docker)

Stellen Sie sicher, dass Docker und Docker Compose installiert sind.

1.  **Projekt klonen:**
    ```bash
    git clone [https://github.com/Dmnk404/css-backend.git](https://github.com/Dmnk404/css-backend.git)
    cd css-backend
    ```

2.  **Container bauen und starten:**
    Dieser Befehl baut das `app`-Image, richtet den `db`-Service ein und startet alles.
    ```bash
    docker-compose up -d --build
    ```

3.  **Migrationen ausführen (Datenbank initialisieren):**
    Nach dem Start müssen die Tabellen erstellt werden (via Alembic):
    ```bash
    docker-compose exec app alembic upgrade head
    ```

## 🧪 Tests ausführen

Die Tests verwenden eine temporäre SQLite-Datenbank, um die PostgreSQL-Datenbank nicht zu beeinträchtigen.

```bash
docker-compose exec app python -m pytest tests/