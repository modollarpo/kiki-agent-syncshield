# KIKI Agent™ Enterprise Deployment Guide

**Version**: 2.0 - Enterprise Edition  
**Date**: February 5, 2026  
**Status**: Production-Ready Architecture

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Prerequisites](#prerequisites)
4. [Local Development](#local-development)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Vault Integration](#vault-integration)
7. [Monitoring & Observability](#monitoring--observability)
8. [Scaling & Performance](#scaling--performance)
9. [Security & Compliance](#security--compliance)
10. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Development (Docker Compose)

```bash
# Clone repository
git clone https://github.com/modollarpo/kiki-agent-syncshield.git
cd kiki-agent-syncshield

# Build all services
docker-compose build

# Start all services
docker-compose up -d

# Check health
curl http://localhost:8080/health/services -H "x-internal-api-key: internal-secret-key"
```

### Production (Kubernetes)

```bash
# Deploy to Kubernetes
./deploy/k8s/deploy.sh

# Verify deployment
kubectl get pods -n kiki-agent

# Access API Gateway
export API_GW=$(kubectl get svc api-gateway -n kiki-agent -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$API_GW/healthz
```

---

## 🏗️ Architecture Overview

### Microservices

| Service | Port | Language | Purpose |
|---------|------|----------|---------|
| **API Gateway** | 8080 | Python | Request routing, authentication |
| **SyncBrain** | 8001 | Python | LLM orchestration, strategy planning |
| **SyncValue** | 8002 | Python | LTV prediction (PyTorch dRNN) |
| **SyncFlow** | 8005 | Go | Real-time bidding (<1ms) |
| **SyncCreate** | 8004 | Python | Creative generation (Stable Diffusion) |
| **SyncEngage** | 8007 | Python | CRM automation |
| **SyncShield** | 8006 | Go | Compliance, audit logging |
| **SyncReflex** | 8003 | Python | Real-time decisioning |
| **SyncTwin** | 8009 | Go | Digital twin modeling |
| **SyncMultimodal** | 8010 | Python | Multimodal AI processing |
| **ExplainabilityBroker** | 8011 | Python | Model explainability (SHAP/LIME) |
| **AcquisitionAgent** | 8012 | Python | User acquisition optimization |

### Infrastructure

- **PostgreSQL 15**: Primary database
- **Redis 7**: Caching & pub/sub
- **MinIO**: Object storage (S3-compatible)

### Communication

- **REST/JSON**: External API, service-to-service
- **gRPC**: High-performance internal calls
- **HTTP/2**: API Gateway to services

---

## 📦 Prerequisites

### Local Development

- Docker 24+ & Docker Compose 2.20+
- 16GB RAM minimum (32GB recommended)
- 50GB disk space
- Python 3.11+ (for local testing)
- Go 1.24+ (for local testing)

### Production Deployment

- Kubernetes 1.28+
- kubectl configured for your cluster
- Helm 3.12+
- HashiCorp Vault 1.15+ (for secret management)
- Persistent volume provisioner (for PostgreSQL/Redis)

---

## 💻 Local Development

### Initial Setup

```bash
# Initialize workspace
./init_workspace.sh

# Build all services
docker-compose build

# Start infrastructure first
docker-compose up -d postgres redis minio

# Wait for databases
sleep 10

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Testing

```bash
# Run tests for specific service
docker-compose exec syncbrain pytest /app/tests/

# Test API endpoints
curl -X POST http://localhost:8001/plan-strategy \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "context": {"goal": "maximize LTV"}}'

# Check Prometheus metrics
curl http://localhost:8001/metrics
```

### Development Workflow

```bash
# Rebuild specific service after code changes
docker-compose build syncbrain

# Restart service
docker-compose up -d syncbrain

# View service logs
docker-compose logs -f syncbrain

# Check health
curl http://localhost:8001/health | jq .
```

---

## ☸️ Kubernetes Deployment

### Step 1: Deploy Infrastructure

```bash
# Apply namespace and base resources
kubectl apply -f deploy/k8s/00-namespace-and-infrastructure.yaml

# Wait for PostgreSQL
kubectl wait --for=condition=ready pod -l app=postgres -n kiki-agent --timeout=180s

# Wait for Redis
kubectl wait --for=condition=ready pod -l app=redis -n kiki-agent --timeout=180s
```

### Step 2: Deploy Core Services

```bash
# Deploy SyncShield (compliance first)
kubectl apply -f deploy/k8s/syncshield-deployment.yaml

# Deploy SyncBrain (orchestration)
kubectl apply -f deploy/k8s/syncbrain-deployment.yaml

# Deploy API Gateway
kubectl apply -f deploy/k8s/api-gateway-deployment.yaml

# Verify deployments
kubectl get deployments -n kiki-agent
kubectl get pods -n kiki-agent
```

### Step 3: Full Deployment Script

```bash
# Automated deployment
./deploy/k8s/deploy.sh

# This script will:
# - Create namespace
# - Deploy infrastructure (PostgreSQL, Redis)
# - Deploy all microservices
# - Configure autoscaling
# - Expose API Gateway as LoadBalancer
```

### Kubernetes Resources Created

```
kiki-agent/
├── Namespace: kiki-agent
├── ConfigMap: kiki-config (shared configuration)
├── Secret: kiki-secrets (WARNING: Replace with Vault!)
├── StatefulSet: postgres (1 replica, 50Gi PV)
├── StatefulSet: redis (1 replica, 10Gi PV)
├── Deployment: api-gateway (3 replicas, HPA 3-20)
├── Deployment: syncbrain (3 replicas, HPA 3-10)
├── Deployment: syncshield (2 replicas, HPA 2-5)
└── Services: ClusterIP for all backend, LoadBalancer for API Gateway
```

---

## 🔐 Vault Integration

### Quick Setup

```bash
# Set Vault address and token
export VAULT_ADDR=http://vault.your-domain.com:8200
export VAULT_TOKEN=your-vault-token

# Run Vault setup script
./deploy/vault-setup.sh

# This will:
# - Enable Kubernetes auth
# - Create Vault policies for each service
# - Create Vault roles
# - Store secrets in Vault
```

### Manual Vault Configuration

```bash
# Enable Kubernetes auth
vault auth enable kubernetes

# Configure Kubernetes backend
vault write auth/kubernetes/config \
    kubernetes_host="https://kubernetes.default.svc:443"

# Create policy for SyncBrain
vault policy write kiki-syncbrain - <<EOF
path "secret/data/kiki-agent/*" {
  capabilities = ["read"]
}
path "secret/data/kiki-agent/openai" {
  capabilities = ["read"]
}
EOF

# Create Kubernetes role
vault write auth/kubernetes/role/syncbrain \
    bound_service_account_names=syncbrain \
    bound_service_account_namespaces=kiki-agent \
    policies=kiki-agent-common,kiki-syncbrain \
    ttl=24h

# Store secrets
vault kv put secret/kiki-agent/openai \
    api_key="sk-YOUR-REAL-KEY"
```

### Update Deployments for Vault

Add annotations to your deployment YAML:

```yaml
metadata:
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "syncbrain"
    vault.hashicorp.com/agent-inject-secret-database: "secret/data/kiki-agent/database"
    vault.hashicorp.com/agent-inject-template-database: |
      {{- with secret "secret/data/kiki-agent/database" -}}
      export DATABASE_URL="{{ .Data.data.url }}"
      {{- end }}
```

---

## 📊 Monitoring & Observability

### Prometheus Metrics

All services expose metrics at `/metrics`:

```bash
# Query Prometheus
kubectl port-forward svc/prometheus -n monitoring 9090:9090

# Example queries
rate(syncbrain_requests_total[5m])
histogram_quantile(0.95, syncvalue_request_latency_seconds)
syncflow_bids_total
```

### Grafana Dashboards

```bash
# Access Grafana
kubectl port-forward svc/grafana -n monitoring 3000:3000

# Import dashboards from deploy/grafana/
# - KIKI Agent Overview
# - Service Performance
# - LTV Prediction Metrics
# - Real-Time Bidding Dashboard
```

### OpenTelemetry Tracing

All requests are traced. Access Jaeger:

```bash
kubectl port-forward svc/jaeger -n monitoring 16686:16686
# Open http://localhost:16686
```

### Logs

```bash
# View logs for specific service
kubectl logs -f deployment/syncbrain -n kiki-agent

# View logs with request ID
kubectl logs deployment/syncbrain -n kiki-agent | grep "request_id=abc123"

# Stream all logs to ELK
# Configure Fluentd/Filebeat for centralized logging
```

---

## 📈 Scaling & Performance

### Horizontal Pod Autoscaling

HPAs are configured for all services:

```bash
# View HPA status
kubectl get hpa -n kiki-agent

# API Gateway: 3-20 replicas (CPU 70%, Memory 80%)
# SyncBrain: 3-10 replicas (CPU 70%)
# SyncShield: 2-5 replicas (CPU 75%)
```

### Vertical Scaling

Update resource requests/limits in deployment YAMLs:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

### Database Scaling

```bash
# Scale PostgreSQL (read replicas)
# Update StatefulSet replicas
kubectl scale statefulset postgres --replicas=3 -n kiki-agent

# Redis clustering
# Deploy Redis Cluster or Sentinel
```

### Load Testing

```bash
# Install k6
brew install k6  # macOS
# or download from https://k6.io/

# Run load test
k6 run deploy/load-tests/api-gateway-test.js
```

---

## 🛡️ Security & Compliance

### Network Policies

```bash
# Apply network policies
kubectl apply -f deploy/k8s/network-policies.yaml

# This restricts:
# - API Gateway: public ingress only
# - Backend services: only from API Gateway
# - Databases: only from backend services
```

### Pod Security

All deployments use:
- `runAsNonRoot: true`
- `readOnlyRootFilesystem: true` (where possible)
- `allowPrivilegeEscalation: false`
- Capability dropping

### TLS/SSL

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f deploy/k8s/cert-issuer.yaml

# TLS will be auto-provisioned for Ingress
```

### Audit Logging

SyncShield logs all compliance events:

```bash
# View audit logs
kubectl exec -it deployment/syncshield -n kiki-agent -- cat /var/log/audit.log

# Export to SIEM
# Configure log forwarding to Splunk/Elastic
```

---

## 🐛 Troubleshooting

### Service Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n kiki-agent

# View logs
kubectl logs <pod-name> -n kiki-agent

# Common issues:
# - ImagePullBackOff: Check image registry
# - CrashLoopBackOff: Check application logs
# - Pending: Check resource availability
```

### Database Connection Issues

```bash
# Test database connectivity
kubectl exec -it deployment/syncbrain -n kiki-agent -- \
  python -c "import psycopg2; psycopg2.connect('postgresql://kiki:kiki_pass@postgres:5432/kiki_db')"

# Check PostgreSQL logs
kubectl logs statefulset/postgres -n kiki-agent
```

### Performance Issues

```bash
# Check resource usage
kubectl top pods -n kiki-agent

# Check HPA status
kubectl describe hpa syncbrain-hpa -n kiki-agent

# View Prometheus alerts
kubectl port-forward svc/prometheus -n monitoring 9090:9090
```

### Health Check Failures

```bash
# Test enhanced health endpoint
export API_GW=$(kubectl get svc api-gateway -n kiki-agent -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$API_GW/health/services -H "x-internal-api-key: internal-secret-key" | jq .

# Check individual service health
kubectl exec -it deployment/syncbrain -n kiki-agent -- curl localhost:8001/health | jq .
```

---

## 📚 Additional Resources

- [Architecture Documentation](./ARCHITECTURE.md)
- [API Reference](./API_REFERENCE.md)
- [Agent Specification](./AGENT_SPEC.md)
- [Owner's Manual](./OWNERS_MANUAL.md)
- [Enterprise Quick Wins](./ENTERPRISE_QUICK_WINS_IMPLEMENTED.md)
- [Enterprise Roadmap](/tmp/enterprise_roadmap.md)

---

## 🎯 Success Criteria

### Development Environment
- ✅ All 12 services running
- ✅ Health checks passing
- ✅ Metrics exposed
- ✅ Request tracing enabled

### Production Kubernetes
- ✅ High availability (multiple replicas)
- ✅ Autoscaling configured
- ✅ Secrets managed via Vault
- ✅ Monitoring & alerting active
- ✅ Network policies enforced
- ✅ TLS/SSL enabled
- ✅ Audit logging enabled

### Performance Targets
- 99.95% uptime SLA
- P95 latency < 200ms
- Error rate < 0.1%
- Successful deployments: multiple per day
- Mean time to recovery < 15 minutes

---

**🚀 KIKI Agent™ is production-ready!**
