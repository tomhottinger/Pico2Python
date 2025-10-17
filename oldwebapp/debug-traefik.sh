#!/bin/bash

echo "=== Traefik Debugging für pico-cms-python ==="
echo ""

echo "1. Container Status:"
docker ps -a | grep pico-cms-python
echo ""

echo "2. Container Logs (letzte 20 Zeilen):"
docker logs --tail 20 pico-cms-python
echo ""

echo "3. Health Check Status:"
docker inspect pico-cms-python | grep -A 10 "Health"
echo ""

echo "4. Netzwerk Verbindungen:"
docker inspect pico-cms-python | grep -A 20 "Networks"
echo ""

echo "5. Ist Container im proxy Netzwerk?"
docker network inspect proxy | grep pico-cms-python
echo ""

echo "6. Traefik Labels:"
docker inspect pico-cms-python | grep -A 30 "Labels"
echo ""

echo "7. Port Test (von Host):"
curl -I http://localhost:5000/health 2>/dev/null || echo "Port nicht erreichbar vom Host"
echo ""

echo "8. Traefik kann Container erreichen?"
docker exec traefik wget -O- --timeout=2 http://pico-cms-python:5000/health 2>/dev/null || echo "Traefik kann Container nicht erreichen"
echo ""

echo "9. DNS Auflösung im Traefik Container:"
docker exec traefik nslookup pico-cms-python 2>/dev/null || echo "DNS Auflösung fehlgeschlagen"
echo ""

echo "=== Mögliche Lösungen ==="
echo ""
echo "Falls Container nicht healthy:"
echo "  docker exec pico-cms-python curl http://localhost:5000/health"
echo ""
echo "Falls nicht im proxy Netzwerk:"
echo "  docker network connect proxy pico-cms-python"
echo ""
echo "Container neu starten:"
echo "  docker-compose down && docker-compose up -d --build"
echo ""
echo "Traefik Logs prüfen:"
echo "  docker logs traefik | grep pypico"
