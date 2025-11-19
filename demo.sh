#!/usr/bin/env bash
# Simple demo script that:
# - runs the seed script in the running container (if using docker-compose)
# - registers a demo user, logs in, extracts JWT, creates a member, lists members
#
# Requirements: docker-compose running the services; jq installed locally for JSON parsing.
set -euo pipefail

# Adjust these if you run the app on a different host/port
BASE_URL="http://localhost:8000"

# Run seed inside container (if using docker-compose)
if docker-compose ps >/dev/null 2>&1; then
  echo "Running seed script inside app container..."
  docker-compose exec -T app python app/scripts/seed.py || true
fi

# Register demo user (may fail if already exists)
echo "Registering demo_user..."
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
  echo "Failed to get token from login response. Exiting."
  exit 1
fi

echo "Got token: ${TOKEN:0:20}... (truncated)"

# Create a member
echo "Creating a demo member..."
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/members" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"first_name":"Demo","last_name":"User","email":"demo.user@example.com","notes":"created by demo.sh"}')
echo "Create response: $CREATE_RESPONSE"

# List members
echo "Listing members (first 10):"
curl -s -X GET "$BASE_URL/members?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN" | jq -C .

echo "Demo finished."
