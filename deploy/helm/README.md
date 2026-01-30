# KIKI Agent™ Helm Chart

## Install/Upgrade
# helm upgrade --install kiki-agent ./deploy/helm --values ./deploy/helm/values.yaml

## Uninstall
# helm uninstall kiki-agent

## Notes
# - Edit values.yaml to set image tags, secrets, and resource limits.
# - Add additional service YAMLs for all microservices as needed.
# - This chart currently deploys only the API Gateway. Extend for all services.
