#!/bin/bash
# KIKI Agent™ Enterprise Setup Script

set -e


# [1/5] Build all Docker containers
echo "[1/5] Building Docker containers..."
docker-compose build

# [2/5] Run DB migrations
echo "[2/5] Running DB migrations..."
# Example: run Alembic, Go migrate, or Prisma for each service as needed
# (Replace with your actual migration commands)
docker-compose run --rm syncbrain alembic upgrade head || true
docker-compose run --rm syncvalue python -m migrate || true
# Add Go migration for syncshield if needed
docker-compose run --rm syncshield go run ./cmd/migrate.go || true

# [3/5] Start Traefik Gateway
echo "[3/5] Starting Traefik Gateway..."
docker-compose up -d traefik

# [4/5] Start all services
echo "[4/5] Starting all services..."
docker-compose up -d

 # [5/5] Health checks for all 6 services
SERVICES=(syncbrain syncvalue syncflow synccreate syncengage syncshield)
HEALTHY=1
SERVICES+=(syncmultimodal) # Adding syncmultimodal to the health check
for SVC in "${SERVICES[@]}"; do
  echo -n "Checking $SVC health... "
  for i in {1..10}; do
    PORT=$(docker-compose port $SVC 8000 | cut -d: -f2)
    STATUS=$(curl -s http://localhost:${PORT}/healthz || true)
    if [[ "$STATUS" == "ok" ]]; then
      echo "healthy"
      break
    fi
    sleep 2
    if [[ $i -eq 10 ]]; then
      echo "FAILED"
      HEALTHY=0
    fi
  done
done

if [[ $HEALTHY -eq 1 ]]; then
  echo "All services are healthy! KIKI Agent™ is ready."
  echo "Access the dashboard at http://localhost:3000"
else
  echo "Some services failed health checks. Please investigate."
  exit 1
fi
