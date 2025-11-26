#!/usr/bin/env bash
# Simple demo script that:
# - runs the seed script in the running container (if using docker-compose)
# - registers a demo user, logs in, extracts JWT, creates a member, lists members
#
# Requirements: docker-compose running the services; jq installed locally for JSON parsing.
set -euo pipefail

BASE_URL="http://localhost:8000"

# Ensure migrations are applied first
echo "Applying migrations (alembic upgrade head)..."
docker-compose exec -T app alembic upgrade head || true

# Run seed inside container (if using docker-compose)
if docker-compose ps >/dev/null 2>&1; then
  echo "Running seed script inside app container..."
  docker-compose exec -T app python app/scripts/seed.py || true
fi

# Register demo user (may fail if already exists)
echo "Registering demo_user (may be skipped if exists)..."
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_user","email":"demo@example.com","password":"demo_pass"}' || true
echo

# Login and extract token
echo "Logging in and extracting JWT..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo_user&password=demo_pass")
echo "Login response: $LOGIN_RESPONSE"
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')

if [ -z "$TOKEN" ]; then
  echo "Failed to get token from login response. Trying admin login..."
  LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=adminpass")
  TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')
  echo "Admin login response: $LOGIN_RESPONSE"
fi

if [ -z "$TOKEN" ]; then
  echo "Failed to get any token. Exiting."
  exit 1
fi

echo "Got token: ${TOKEN:0:20}... (truncated)"

# List members
echo "Listing members (first 10):"
curl -s -X GET "$BASE_URL/members?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN" | jq -C .

echo "Demo finished."
