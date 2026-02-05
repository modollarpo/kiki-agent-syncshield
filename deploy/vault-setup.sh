#!/bin/bash

# HashiCorp Vault Integration Setup for KIKI Agent™
# Quick Win: Eliminate hardcoded secrets

set -e

echo "🔐 Vault Integration Setup for KIKI Agent™"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
VAULT_NAMESPACE="kiki-agent"
K8S_NAMESPACE="kiki-agent"

echo -e "${YELLOW}This script will:${NC}"
echo "  1. Enable Kubernetes auth in Vault"
echo "  2. Create Vault policies for KIKI Agent services"
echo "  3. Create Vault roles for service accounts"
echo "  4. Store secrets in Vault"
echo "  5. Deploy Vault Agent injector to Kubernetes"
echo ""

# Check if Vault is available
if ! command -v vault &> /dev/null; then
    echo -e "${RED}❌ Vault CLI not found. Please install Vault first.${NC}"
    echo "   Visit: https://www.vaultproject.io/downloads"
    exit 1
fi

# Check Vault connectivity
echo -e "${YELLOW}Checking Vault connectivity...${NC}"
if ! vault status &> /dev/null; then
    echo -e "${RED}❌ Cannot connect to Vault at ${VAULT_ADDR}${NC}"
    echo "   Set VAULT_ADDR and VAULT_TOKEN environment variables"
    exit 1
fi
echo -e "${GREEN}✅ Connected to Vault${NC}"

# Enable Kubernetes auth
echo -e "${YELLOW}Enabling Kubernetes authentication...${NC}"
vault auth enable -path=kubernetes kubernetes 2>/dev/null || echo "Already enabled"

# Configure Kubernetes auth
echo -e "${YELLOW}Configuring Kubernetes auth backend...${NC}"
vault write auth/kubernetes/config \
    kubernetes_host="https://kubernetes.default.svc:443"

# Create Vault policy for KIKI Agent services
echo -e "${YELLOW}Creating Vault policies...${NC}"

# Policy for all services (read common secrets)
vault policy write kiki-agent-common - <<EOF
# Read common database credentials
path "secret/data/kiki-agent/database" {
  capabilities = ["read"]
}

# Read Redis credentials
path "secret/data/kiki-agent/redis" {
  capabilities = ["read"]
}

# Read JWT secret
path "secret/data/kiki-agent/jwt" {
  capabilities = ["read"]
}

# Read internal API key
path "secret/data/kiki-agent/internal-api-key" {
  capabilities = ["read"]
}
EOF

# Policy for SyncBrain (needs OpenAI key)
vault policy write kiki-syncbrain - <<EOF
# Include common policy
path "secret/data/kiki-agent/*" {
  capabilities = ["read"]
}

# Read OpenAI API key
path "secret/data/kiki-agent/openai" {
  capabilities = ["read"]
}
EOF

# Policy for SyncCreate (needs creative API keys)
vault policy write kiki-synccreate - <<EOF
# Include common policy
path "secret/data/kiki-agent/*" {
  capabilities = ["read"]
}

# Read Stability AI key
path "secret/data/kiki-agent/stability" {
  capabilities = ["read"]
}

# Read Runway ML key
path "secret/data/kiki-agent/runway" {
  capabilities = ["read"]
}
EOF

# Policy for SyncShield (needs encryption key)
vault policy write kiki-syncshield - <<EOF
# Include common policy
path "secret/data/kiki-agent/*" {
  capabilities = ["read"]
}

# Read encryption key
path "secret/data/kiki-agent/encryption" {
  capabilities = ["read"]
}
EOF

echo -e "${GREEN}✅ Policies created${NC}"

# Create Vault roles for each service
echo -e "${YELLOW}Creating Vault roles...${NC}"

for service in syncbrain syncvalue syncflow synccreate syncengage syncshield syncreflex synctwin syncmultimodal; do
    vault write auth/kubernetes/role/$service \
        bound_service_account_names=$service \
        bound_service_account_namespaces=$K8S_NAMESPACE \
        policies=kiki-agent-common,kiki-$service \
        ttl=24h
done

echo -e "${GREEN}✅ Roles created${NC}"

# Store secrets in Vault
echo -e "${YELLOW}Storing secrets in Vault...${NC}"
echo -e "${RED}⚠️  WARNING: These are example secrets. Replace with real values!${NC}"

# Database
vault kv put secret/kiki-agent/database \
    url="postgresql://kiki:CHANGEME@postgres:5432/kiki_db" \
    username="kiki" \
    password="CHANGEME_SECURE_PASSWORD"

# Redis
vault kv put secret/kiki-agent/redis \
    url="redis://redis:6379/0" \
    password=""

# JWT
vault kv put secret/kiki-agent/jwt \
    secret="CHANGE-THIS-TO-RANDOM-256-BIT-KEY" \
    algorithm="HS256" \
    expiration_minutes="60"

# Internal API key
vault kv put secret/kiki-agent/internal-api-key \
    key="CHANGE-THIS-TO-RANDOM-API-KEY"

# OpenAI (for SyncBrain)
vault kv put secret/kiki-agent/openai \
    api_key="sk-REPLACE-WITH-REAL-OPENAI-KEY" \
    model="gpt-4" \
    max_tokens="2000"

# Stability AI (for SyncCreate)
vault kv put secret/kiki-agent/stability \
    api_key="REPLACE-WITH-REAL-STABILITY-KEY"

# Runway ML (for SyncCreate)
vault kv put secret/kiki-agent/runway \
    api_key="REPLACE-WITH-REAL-RUNWAY-KEY"

# Encryption key (for SyncShield)
vault kv put secret/kiki-agent/encryption \
    key="REPLACE-WITH-REAL-32-BYTE-KEY!!"

echo -e "${GREEN}✅ Secrets stored in Vault${NC}"

# Deploy Vault Agent Injector to Kubernetes
echo -e "${YELLOW}Deploying Vault Agent Injector to Kubernetes...${NC}"
echo "Run this command to install Vault via Helm:"
echo ""
echo "  helm repo add hashicorp https://helm.releases.hashicorp.com"
echo "  helm repo update"
echo "  helm install vault hashicorp/vault \\"
echo "    --namespace kiki-agent \\"
echo "    --set 'injector.enabled=true' \\"
echo "    --set 'server.dev.enabled=true'"
echo ""

echo -e "${GREEN}✅ Vault integration setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Update deployment YAMLs with Vault annotations"
echo "  2. Create ServiceAccounts for each service"
echo "  3. Add Vault agent sidecar annotations to pods"
echo "  4. Replace Secret resources with Vault references"
echo ""
echo -e "${YELLOW}Example Vault annotations for deployment:${NC}"
cat <<EOF

metadata:
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "syncbrain"
    vault.hashicorp.com/agent-inject-secret-database: "secret/data/kiki-agent/database"
    vault.hashicorp.com/agent-inject-template-database: |
      {{- with secret "secret/data/kiki-agent/database" -}}
      export DATABASE_URL="{{ .Data.data.url }}"
      {{- end }}
EOF

echo ""
echo -e "${GREEN}🔐 Vault setup complete!${NC}"
