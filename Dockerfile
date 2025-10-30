FROM python:3.12-slim

WORKDIR /app

# System-Abhängigkeiten für PostgreSQL und Build-Tools
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    # Hinzugefügt: Die notwendigen Python-Header für die Kompilierung von Kryptografie-Paketen
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Die Installation wird jetzt erfolgreich die nativen Teile von cryptography bauen
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]