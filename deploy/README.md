# Deploy

This folder contains Docker Compose, Kubernetes manifests, and CI/CD scripts for deploying the KIKI Agent™ platform.# Deploy

- Kubernetes manifests, Helm charts, CI/CD workflows, and Terraform scripts

## Monitoring
- Prometheus scrapes /metrics endpoints on all services (see prometheus.yml).
- Grafana dashboards can be created for request rates, error rates, and latency.

## Rate Limiting & Logging
- API Gateway enforces 60 requests/minute per IP.
- All requests are logged with method, path, and client IP.

## Deployment Automation
- Use `make build` and `make up` for local Docker Compose.
- Use `make deploy` for Kubernetes (Helm charts for all services).
- CI/CD workflows run tests and can be extended for cloud deploys.

## Extending
- Add /metrics endpoint to all Python/Go services using prometheus_client or Prometheus Go client.
- Add Grafana dashboards for business and system metrics.
- Add cloud provider-specific deploy scripts as needed.
