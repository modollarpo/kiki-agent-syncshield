# Azure AKS Automated Deployment Script for KIKI Agent Platform (PowerShell)
# This script provisions AKS, ACR, builds/pushes images, and deploys manifests.
# Prerequisites: Azure CLI, Docker, kubectl, and Terraform installed and logged in.

# 1. Set variables
$RESOURCE_GROUP = "kiki-rg"
$LOCATION = "eastus"
$ACR_NAME = "kikiregistry"
$AKS_NAME = "kiki-aks"

# 2. Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# 3. Create Azure Container Registry
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic

# 4. Create AKS cluster and attach ACR
az aks create --resource-group $RESOURCE_GROUP --name $AKS_NAME --node-count 3 --enable-addons monitoring --generate-ssh-keys --attach-acr $ACR_NAME

# 5. Get AKS credentials
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_NAME

# 6. Auto-detect and build/push Docker images for all services with a Dockerfile
az acr login --name $ACR_NAME
$dockerfiles = Get-ChildItem -Path "services" -Recurse -Filter "Dockerfile"
foreach ($dockerfile in $dockerfiles) {
    $service = Split-Path $dockerfile.DirectoryName -Leaf
    Write-Host "Building and pushing $service..."
    docker build -t "$ACR_NAME.azurecr.io/$service:latest" -f $dockerfile.FullName .
    docker push "$ACR_NAME.azurecr.io/$service:latest"
}

# 7. Deploy Kubernetes manifests
kubectl apply -f deploy/k8s/

# 8. (Optional) Deploy ingress
kubectl apply -f deploy/k8s-ingress.yaml

# 9. Monitor deployment
kubectl get pods -A
az aks browse --resource-group $RESOURCE_GROUP --name $AKS_NAME

# 10. Set environment variables/secrets as needed
# Use Azure Key Vault or kubectl create secret

# End of script
