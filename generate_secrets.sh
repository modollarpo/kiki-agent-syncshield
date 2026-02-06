#!/bin/bash
# Generate Secure Secrets for KIKI Agent™
#
# Run this script to generate cryptographically secure secrets for .env file.
# Copy output to your .env file.

set -e

echo "=================================================="
echo "KIKI Agent™ - Secure Secret Generator"
echo "=================================================="
echo ""
echo "Copy these values to your .env file:"
echo ""
echo "# Generated on $(date)"
echo ""

# JWT Secret (64 characters recommended)
KIKI_JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
echo "KIKI_JWT_SECRET=$KIKI_JWT_SECRET"

# Internal API Key (32 characters)
INTERNAL_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "INTERNAL_API_KEY=$INTERNAL_API_KEY"

# Legacy JWT Secret (backward compatibility)
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "JWT_SECRET=$JWT_SECRET"

# Service API Keys
echo ""
echo "# Service-to-Service API Keys"
SYNCFLOW_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "SYNCFLOW_API_KEY=$SYNCFLOW_API_KEY"

SYNCBRAIN_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "SYNCBRAIN_API_KEY=$SYNCBRAIN_API_KEY"

SYNCCREATE_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "SYNCCREATE_API_KEY=$SYNCCREATE_API_KEY"

SYNCSHIELD_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "SYNCSHIELD_API_KEY=$SYNCSHIELD_API_KEY"

echo ""
echo "=================================================="
echo "✓ Secrets generated successfully!"
echo ""
echo "⚠️  IMPORTANT SECURITY NOTES:"
echo "  1. Never commit .env file to git"
echo "  2. Store secrets securely (password manager/vault)"
echo "  3. Rotate secrets periodically (every 90 days)"
echo "  4. Use different secrets for dev/staging/production"
echo "=================================================="
