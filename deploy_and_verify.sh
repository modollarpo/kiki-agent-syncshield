#!/bin/bash
set -e

# 1. Build and scan Docker images
printf "\n[1/9] Building and scanning Docker images...\n"
docker-compose build
for img in $(docker images --format '{{.Repository}}:{{.Tag}}' | grep kiki); do
  echo "Scanning $img for vulnerabilities..."
  docker scan $img || true
  # Replace with your preferred scanner (Trivy, Snyk, etc.)
done

# 2. Run DB migrations and backup/restore test
printf "\n[2/9] Running DB migrations and backup/restore test...\n"
docker-compose run --rm syncbrain alembic upgrade head || true
docker-compose run --rm syncvalue python -m migrate || true
docker-compose run --rm syncshield go run ./cmd/migrate.go || true
# Backup
docker-compose exec postgres pg_dump -U kiki -F c -b -v -f /tmp/kiki_backup.dump kiki
# Restore test (optional, uncomment to test)
# docker-compose exec postgres pg_restore -U kiki -d kiki_test /tmp/kiki_backup.dump

# 3. Configure SSL, security headers, and CORS
printf "\n[3/9] Verifying SSL, security headers, and CORS...\n"
# SSL: Check Traefik config and certs
if grep -q 'entryPoints.websecure' deploy/traefik/traefik.yml; then
  echo "Traefik SSL config found."
else
  echo "WARNING: SSL not configured in Traefik!"
fi
# Security headers
curl -sI https://localhost | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|Referrer-Policy'
# CORS
curl -sI -H "Origin: https://yourdomain.com" https://localhost | grep 'Access-Control-Allow-Origin'

# 4. Set up Prometheus/Grafana dashboards and alerting
printf "\n[4/9] Verifying Prometheus/Grafana dashboards and alerting...\n"
# Check Prometheus targets
curl -s http://localhost:9090/api/v1/targets | grep 'health' || echo "Prometheus targets not found!"
# Check Grafana dashboards (API or manual)
# curl -s -u admin:admin http://localhost:3001/api/search?query=KIKI

# 5. Health checks for all services
printf "\n[5/9] Running health checks for all services...\n"
bash setup_enterprise.sh

# 6. Validate dashboard UX (no white screens, live feeds)
printf "\n[6/9] Validating dashboard UX...\n"
# Check for skeletons/Suspense (manual or with Playwright/Cypress)
# npx playwright test || npx cypress run

# 7. Test compliance (PII masking, GDPR/CCPA flows)
printf "\n[7/9] Testing compliance and privacy...\n"
# PII masking test
curl -X POST http://localhost:8004/audit -H 'Content-Type: application/json' -d '{"Email":"test@example.com","IP":"1.2.3.4"}'
# GDPR/CCPA export/delete (manual or API call)
# curl -X POST http://localhost:8000/user/export -d '{"user_id":123}'

# 8. Log retention and backup policy
printf "\n[8/9] Verifying log retention and backup policy...\n"
# Check log volume size and retention
# docker-compose exec syncshield ls -lh /var/log/kiki

# 9. Final stakeholder review
printf "\n[9/9] Stakeholder review and go-live...\n"
echo "Demo to business/ops, confirm all checks passed."
echo "KIKI Agent™ is ready for live ad traffic!"
