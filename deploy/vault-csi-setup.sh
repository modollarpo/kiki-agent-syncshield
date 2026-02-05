#!/bin/bash
#
# Vault CSI Driver Setup for Kubernetes
# Migrates K8s secrets to HashiCorp Vault with CSI integration
#

set -e

echo "🔐 KIKI Agent™ Vault CSI Driver Setup"
echo "========================================"
echo ""

# Configuration
VAULT_ADDR="${VAULT_ADDR:-http://vault:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-root}"
export VAULT_ADDR
export VAULT_TOKEN

NAMESPACE="${KUBERNETES_NAMESPACE:-kiki-agent}"
K8S_HOST="${KUBERNETES_SERVICE_HOST:-https://kubernetes.default.svc}"

echo "📋 Configuration:"
echo "  Vault Address: $VAULT_ADDR"
echo "  Namespace: $NAMESPACE"
echo "  K8s Host: $K8S_HOST"
echo ""

# Step 1: Install Vault CSI Driver (Helm)
echo "📦 Step 1: Installing Vault CSI Driver via Helm..."
if ! helm repo list | grep -q hashicorp; then
    helm repo add hashicorp https://helm.releases.hashicorp.com
fi
helm repo update

helm upgrade --install vault-csi-provider hashicorp/vault-csi-provider \
    --namespace kiki-agent --create-namespace \
    --set "vault.address=$VAULT_ADDR" \
    --set "vault.authPath=auth/kubernetes"

echo "✅ Vault CSI Driver installed"
echo ""

# Step 2: Enable Kubernetes auth method if not already enabled
echo "🔧 Step 2: Configuring Vault Kubernetes auth..."
vault auth list | grep -q 'kubernetes/' || vault auth enable kubernetes

# Configure Kubernetes auth
kubectl create serviceaccount vault-auth -n "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Create secret for service account (K8s 1.24+)
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: vault-auth-token
  namespace: $NAMESPACE
  annotations:
    kubernetes.io/service-account.name: vault-auth
type: kubernetes.io/service-account-token
EOF

# Wait for token
sleep 5

# Get the token reviewer JWT
TOKEN_REVIEW_JWT=$(kubectl get secret vault-auth-token -n "$NAMESPACE" -o jsonpath='{.data.token}' | base64 --decode)
K8S_CA_CERT=$(kubectl config view --raw --minify --flatten -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' | base64 --decode)

# Configure Vault to talk to Kubernetes
vault write auth/kubernetes/config \
    token_reviewer_jwt="$TOKEN_REVIEW_JWT" \
    kubernetes_host="$K8S_HOST" \
    kubernetes_ca_cert="$K8S_CA_CERT" \
    disable_iss_validation=true

echo "✅ Kubernetes auth configured"
echo ""

# Step 3: Create Vault policies for KIKI services
echo "📝 Step 3: Creating Vault policies..."

# SyncBrain policy
vault policy write syncbrain - <<EOF
path "secret/data/kiki-agent/syncbrain/*" {
  capabilities = ["read", "list"]
}
path "secret/data/kiki-agent/common/*" {
  capabilities = ["read", "list"]
}
EOF

# SyncValue policy
vault policy write syncvalue - <<EOF
path "secret/data/kiki-agent/syncvalue/*" {
  capabilities = ["read", "list"]
}
path "secret/data/kiki-agent/common/*" {
  capabilities = ["read", "list"]
}
EOF

# SyncFlow policy
vault policy write syncflow - <<EOF
path "secret/data/kiki-agent/syncflow/*" {
  capabilities = ["read", "list"]
}
path "secret/data/kiki-agent/common/*" {
  capabilities = ["read", "list"]
}
EOF

# Common policy for all services
vault policy write kiki-common - <<EOF
path "secret/data/kiki-agent/common/*" {
  capabilities = ["read", "list"]
}
path "secret/data/kiki-agent/database" {
  capabilities = ["read"]
}
path "secret/data/kiki-agent/redis" {
  capabilities = ["read"]
}
EOF

echo "✅ Vault policies created"
echo ""

# Step 4: Create Kubernetes auth roles
echo "🔑 Step 4: Creating Kubernetes auth roles..."

# Create role for each service
for service in syncbrain syncvalue syncflow synccreate syncengage syncshield synctwin syncreflex syncmultimodal syncportal acquisitionagent explainability-broker api-gateway; do
    vault write auth/kubernetes/role/$service \
        bound_service_account_names=$service \
        bound_service_account_namespaces=$NAMESPACE \
        policies=kiki-common,$service \
        ttl=24h
    echo "  ✓ Created role for $service"
done

echo "✅ All Kubernetes auth roles created"
echo ""

# Step 5: Store secrets in Vault
echo "💾 Step 5: Storing secrets in Vault..."

# Common secrets
vault kv put secret/kiki-agent/common/jwt \
    secret_key="$(openssl rand -base64 32)" \
    algorithm="HS256"

vault kv put secret/kiki-agent/database \
    host="postgres" \
    port="5432" \
    database="kiki_db" \
    username="kiki" \
    password="kiki_pass"

vault kv put secret/kiki-agent/redis \
    host="redis" \
    port="6379" \
    password=""

# SyncBrain secrets
vault kv put secret/kiki-agent/syncbrain/openai \
    api_key="${OPENAI_API_KEY:-demo-key}" \
    model="gpt-4" \
    max_tokens="2000"

# SyncValue secrets
vault kv put secret/kiki-agent/syncvalue/model \
    path="ltv_model.pt" \
    input_size="10" \
    hidden_size="16"

# SyncFlow secrets
vault kv put secret/kiki-agent/syncflow/bidding \
    timeout_ms="100" \
    max_bid="10.0" \
    min_bid="0.01"

# SyncCreate secrets
vault kv put secret/kiki-agent/synccreate/api \
    stability_api_key="${STABILITY_API_KEY:-}" \
    runway_api_key="${RUNWAY_API_KEY:-}"

# SyncEngage secrets
vault kv put secret/kiki-agent/syncengage/crm \
    hubspot_api_key="${HUBSPOT_API_KEY:-}" \
    salesforce_api_key="${SALESFORCE_API_KEY:-}"

# SyncShield secrets
vault kv put secret/kiki-agent/syncshield/encryption \
    key="$(openssl rand -base64 32)" \
    algorithm="AES-256-GCM"

echo "✅ All secrets stored in Vault"
echo ""

# Step 6: Create Kubernetes SecretProviderClass resources
echo "📄 Step 6: Creating SecretProviderClass resources..."

cat > /tmp/vault-secret-provider-class.yaml <<EOF
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: vault-database
  namespace: $NAMESPACE
spec:
  provider: vault
  parameters:
    vaultAddress: "$VAULT_ADDR"
    roleName: "kiki-common"
    objects: |
      - objectName: "db-host"
        secretPath: "secret/data/kiki-agent/database"
        secretKey: "host"
      - objectName: "db-port"
        secretPath: "secret/data/kiki-agent/database"
        secretKey: "port"
      - objectName: "db-name"
        secretPath: "secret/data/kiki-agent/database"
        secretKey: "database"
      - objectName: "db-username"
        secretPath: "secret/data/kiki-agent/database"
        secretKey: "username"
      - objectName: "db-password"
        secretPath: "secret/data/kiki-agent/database"
        secretKey: "password"
  secretObjects:
  - secretName: postgres-credentials
    type: Opaque
    data:
    - objectName: db-host
      key: host
    - objectName: db-port
      key: port
    - objectName: db-name
      key: database
    - objectName: db-username
      key: username
    - objectName: db-password
      key: password
---
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: vault-syncbrain
  namespace: $NAMESPACE
spec:
  provider: vault
  parameters:
    vaultAddress: "$VAULT_ADDR"
    roleName: "syncbrain"
    objects: |
      - objectName: "openai-api-key"
        secretPath: "secret/data/kiki-agent/syncbrain/openai"
        secretKey: "api_key"
      - objectName: "jwt-secret"
        secretPath: "secret/data/kiki-agent/common/jwt"
        secretKey: "secret_key"
  secretObjects:
  - secretName: syncbrain-secrets
    type: Opaque
    data:
    - objectName: openai-api-key
      key: openai_api_key
    - objectName: jwt-secret
      key: jwt_secret
---
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: vault-syncshield
  namespace: $NAMESPACE
spec:
  provider: vault
  parameters:
    vaultAddress: "$VAULT_ADDR"
    roleName: "syncshield"
    objects: |
      - objectName: "encryption-key"
        secretPath: "secret/data/kiki-agent/syncshield/encryption"
        secretKey: "key"
  secretObjects:
  - secretName: syncshield-secrets
    type: Opaque
    data:
    - objectName: encryption-key
      key: encryption_key
EOF

kubectl apply -f /tmp/vault-secret-provider-class.yaml
rm /tmp/vault-secret-provider-class.yaml

echo "✅ SecretProviderClass resources created"
echo ""

# Step 7: Verify setup
echo "🔍 Step 7: Verifying Vault CSI setup..."
kubectl get csidriver -n $NAMESPACE
kubectl get secretproviderclass -n $NAMESPACE

echo ""
echo "✅ Vault CSI Driver setup complete!"
echo ""
echo "📚 Next Steps:"
echo "  1. Update deployments to use CSI volumes:"
echo "     - Add serviceAccount with Vault role"
echo "     - Mount CSI volume with SecretProviderClass"
echo "     - Reference secrets from mounted path or K8s secrets"
echo ""
echo "  2. Remove hardcoded secrets from K8s manifests"
echo ""
echo "  3. Test secret injection:"
echo "     kubectl exec -it <pod> -n $NAMESPACE -- env | grep SECRET"
echo ""
echo "🔐 Vault UI: $VAULT_ADDR/ui"
echo "🔑 Vault Token: $VAULT_TOKEN"
echo ""
