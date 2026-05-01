#!/bin/bash

BASE_URL="http://127.0.0.1:8000/api"

echo "=== 1. Intentar acceder sin token ==="
curl -s $BASE_URL/socios/ | jq .

echo -e "\n=== 2. Obtener tokens (login) ==="
TOKENS=$(curl -s -X POST $BASE_URL/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "isard", "password": "pirineus"}')

echo $TOKENS | jq .
ACCESS=$(echo $TOKENS | jq -r '.access')
REFRESH=$(echo $TOKENS | jq -r '.refresh')

echo -e "\n=== 3. Acceder con token ==="
curl -s $BASE_URL/socios/ \
  -H "Authorization: Bearer $ACCESS" | jq .

echo -e "\n=== 4. Logout (invalidar refresh) ==="
curl -s -X POST $BASE_URL/socios/auth/logout/ \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH\"}" | jq .

echo -e "\n=== 5. Intentar usar refresh token invalidado ==="
curl -s -X POST $BASE_URL/token/refresh/ \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH\"}" | jq .
