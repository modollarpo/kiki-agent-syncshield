#!/bin/bash

# KIKI Agent™ Kubernetes Deployment Script
# Deploys all services to Kubernetes cluster

set -e

echo "🚀 KIKI Agent™ Kubernetes Deployment"
echo "===================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="kiki-agent"
KUBECTL_CMD="kubectl"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found. Please install kubectl first.${NC}"
    exit 1
fi

# Check cluster connectivity
echo -e "${YELLOW}Checking cluster connectivity...${NC}"
if ! $KUBECTL_CMD cluster-info &> /dev/null; then
    echo -e "${RED}❌ Cannot connect to Kubernetes cluster${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Connected to cluster${NC}"

# Create namespace and base infrastructure
echo -e "${YELLOW}Creating namespace and infrastructure...${NC}"
$KUBECTL_CMD apply -f deploy/k8s/00-namespace-and-infrastructure.yaml

# Wait for PostgreSQL and Redis
echo -e "${YELLOW}Waiting for database and cache...${NC}"
$KUBECTL_CMD wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=180s
$KUBECTL_CMD wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=180s
echo -e "${GREEN}✅ Infrastructure ready${NC}"

# Deploy core services
echo -e "${YELLOW}Deploying SyncShield (Compliance)...${NC}"
$KUBECTL_CMD apply -f deploy/k8s/syncshield-deployment.yaml
sleep 5

echo -e "${YELLOW}Deploying SyncBrain (Orchestration)...${NC}"
$KUBECTL_CMD apply -f deploy/k8s/syncbrain-deployment.yaml
sleep 5

echo -e "${YELLOW}Deploying API Gateway...${NC}"
$KUBECTL_CMD apply -f deploy/k8s/api-gateway-deployment.yaml
sleep 5

# Wait for deployments
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
$KUBECTL_CMD wait --for=condition=available deployment -l tier=backend -n $NAMESPACE --timeout=300s
$KUBECTL_CMD wait --for=condition=available deployment -l tier=frontend -n $NAMESPACE --timeout=300s

echo -e "${GREEN}✅ All services deployed successfully!${NC}"

# Show deployment status
echo ""
echo -e "${YELLOW}Deployment Status:${NC}"
$KUBECTL_CMD get deployments -n $NAMESPACE
echo ""
$KUBECTL_CMD get pods -n $NAMESPACE
echo ""
$KUBECTL_CMD get svc -n $NAMESPACE

# Get API Gateway external IP
echo ""
echo -e "${YELLOW}Waiting for API Gateway external IP...${NC}"
EXTERNAL_IP=""
while [ -z $EXTERNAL_IP ]; do
    echo "Waiting for LoadBalancer..."
    EXTERNAL_IP=$($KUBECTL_CMD get svc api-gateway -n $NAMESPACE --template="{{range .status.loadBalancer.ingress}}{{.ip}}{{end}}")
    [ -z "$EXTERNAL_IP" ] && sleep 10
done

echo -e "${GREEN}✅ API Gateway available at: http://${EXTERNAL_IP}${NC}"
echo ""
echo -e "${YELLOW}Test with:${NC}"
echo "  curl http://${EXTERNAL_IP}/healthz"
echo "  curl http://${EXTERNAL_IP}/health/services -H 'x-internal-api-key: CHANGE-THIS-INTERNAL-KEY'"
echo ""
echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Update secrets in deploy/k8s/00-namespace-and-infrastructure.yaml"
echo "  2. Integrate with HashiCorp Vault for secret management"
echo "  3. Configure Ingress for domain routing"
echo "  4. Set up monitoring with Prometheus/Grafana"
echo "  5. Configure alerts with PagerDuty"
