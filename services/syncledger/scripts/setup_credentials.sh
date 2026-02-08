#!/bin/bash
# Credential Setup Script for Multi-Platform Integration
# Helps configure .env file with API credentials for all 6 platforms

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "================================================================================"
echo " KIKI Agent™ - Multi-Platform Credential Setup"
echo "================================================================================"
echo ""

ENV_FILE="/workspaces/kiki-agent-syncshield/.env"

# Check if .env exists, create if not
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  .env file not found, creating new one...${NC}"
    touch "$ENV_FILE"
fi

# Backup existing .env
BACKUP_FILE="${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$ENV_FILE" "$BACKUP_FILE"
echo -e "${GREEN}✅ Backed up existing .env to: $BACKUP_FILE${NC}"
echo ""

echo "This script will help you configure API credentials for 6 ad platforms:"
echo "  1. Meta Ads (Facebook/Instagram)"
echo "  2. Google Ads"
echo "  3. TikTok Ads 🆕"
echo "  4. LinkedIn Ads 🆕"
echo "  5. Amazon Advertising 🆕"
echo "  6. Microsoft Advertising (Bing) 🆕"
echo ""
echo -e "${YELLOW}Note: You can skip any platform by pressing Enter${NC}"
echo ""

# Function to add/update env variable
update_env() {
    local key=$1
    local value=$2
    
    if grep -q "^${key}=" "$ENV_FILE"; then
        # Update existing
        sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
    else
        # Add new
        echo "${key}=${value}" >> "$ENV_FILE"
    fi
}

# Function to prompt for credential
prompt_credential() {
    local platform=$1
    local var_name=$2
    local description=$3
    local example=$4
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}$platform${NC}"
    echo "$description"
    if [ -n "$example" ]; then
        echo -e "Example: ${YELLOW}$example${NC}"
    fi
    echo ""
    
    # Check if already exists
    if grep -q "^${var_name}=" "$ENV_FILE"; then
        current_value=$(grep "^${var_name}=" "$ENV_FILE" | cut -d '=' -f2)
        echo -e "Current value: ${YELLOW}$current_value${NC}"
        read -p "Enter new value (or press Enter to keep current): " new_value
        if [ -z "$new_value" ]; then
            echo -e "${GREEN}✅ Keeping current value${NC}"
            echo ""
            return
        fi
    else
        read -p "Enter value (or press Enter to skip): " new_value
        if [ -z "$new_value" ]; then
            echo -e "${YELLOW}⏭️  Skipped${NC}"
            echo ""
            return
        fi
    fi
    
    update_env "$var_name" "$new_value"
    echo -e "${GREEN}✅ Updated $var_name${NC}"
    echo ""
}

# Meta Ads
prompt_credential \
    "1. META ADS (Facebook/Instagram)" \
    "META_APP_ID" \
    "Get credentials at: https://developers.facebook.com/apps" \
    "1234567890123456"

prompt_credential \
    "1. META ADS (continued)" \
    "META_APP_SECRET" \
    "App Secret from Facebook App Dashboard" \
    "abcdef1234567890abcdef1234567890"

prompt_credential \
    "1. META ADS (continued)" \
    "META_ACCESS_TOKEN" \
    "Long-lived user access token (get via Graph API Explorer)" \
    "EAABsbCS1iHgBO7ZC..."

# Google Ads
prompt_credential \
    "2. GOOGLE ADS" \
    "GOOGLE_ADS_CREDENTIALS_PATH" \
    "Path to google-ads.yaml file (or leave default)" \
    "/etc/kiki/google-ads.yaml"

# TikTok Ads
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}3. TIKTOK ADS 🆕${NC}"
echo "Get credentials at: https://ads.tiktok.com/marketing_api/apps"
echo ""
echo -e "${YELLOW}Setup Instructions:${NC}"
echo "  1. Go to TikTok Ads Manager > Tools > Marketing API"
echo "  2. Create new app or use existing app"
echo "  3. Copy App ID and generate Access Token"
echo "  4. Required permissions: advertiser.read, advertiser.data.read, reporting.read"
echo ""

prompt_credential \
    "3. TIKTOK ADS (App ID)" \
    "TIKTOK_APP_ID" \
    "TikTok App ID (numeric)" \
    "1234567890"

prompt_credential \
    "3. TIKTOK ADS (App Secret)" \
    "TIKTOK_APP_SECRET" \
    "TikTok App Secret" \
    "abc123def456..."

prompt_credential \
    "3. TIKTOK ADS (Access Token)" \
    "TIKTOK_ACCESS_TOKEN" \
    "TikTok Long-term Access Token (90-day expiration)" \
    "a1b2c3d4e5f6..."

# LinkedIn Ads
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}4. LINKEDIN ADS 🆕${NC}"
echo "Get credentials at: https://www.linkedin.com/developers/apps"
echo ""
echo -e "${YELLOW}Setup Instructions:${NC}"
echo "  1. Create LinkedIn Developer App"
echo "  2. Add 'Advertising API' product"
echo "  3. Request access for r_ads and rw_ads scopes"
echo "  4. Generate OAuth 2.0 access token"
echo ""

prompt_credential \
    "4. LINKEDIN ADS (Client ID)" \
    "LINKEDIN_CLIENT_ID" \
    "LinkedIn Client ID" \
    "77abcd1234567890"

prompt_credential \
    "4. LINKEDIN ADS (Client Secret)" \
    "LINKEDIN_CLIENT_SECRET" \
    "LinkedIn Client Secret" \
    "AbCdEf123456"

prompt_credential \
    "4. LINKEDIN ADS (Access Token)" \
    "LINKEDIN_ACCESS_TOKEN" \
    "LinkedIn Access Token (60-day expiration)" \
    "AQV123abc..."

# Amazon Advertising
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}5. AMAZON ADVERTISING 🆕${NC}"
echo "Get credentials at: https://advertising.amazon.com/API"
echo ""
echo -e "${YELLOW}Setup Instructions:${NC}"
echo "  1. Request Amazon Advertising API access"
echo "  2. Create Login with Amazon (LWA) credentials"
echo "  3. Authorize app for Sponsored Ads API"
echo ""

prompt_credential \
    "5. AMAZON ADS (Client ID)" \
    "AMAZON_CLIENT_ID" \
    "Amazon LWA Client ID" \
    "amzn1.application-oa2-client.abc123"

prompt_credential \
    "5. AMAZON ADS (Client Secret)" \
    "AMAZON_CLIENT_SECRET" \
    "Amazon LWA Client Secret" \
    "abc123def456..."

prompt_credential \
    "5. AMAZON ADS (Access Token)" \
    "AMAZON_ACCESS_TOKEN" \
    "Amazon Access Token (starts with Atza|)" \
    "Atza|IQEBLjAsAhQ..."

prompt_credential \
    "5. AMAZON ADS (Refresh Token)" \
    "AMAZON_REFRESH_TOKEN" \
    "Amazon Refresh Token (starts with Atzr|)" \
    "Atzr|IQEBLzAtAhU..."

# Microsoft Advertising
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}6. MICROSOFT ADVERTISING (Bing) 🆕${NC}"
echo "Get credentials at: https://learn.microsoft.com/en-us/advertising/guides/get-started"
echo ""
echo -e "${YELLOW}Setup Instructions:${NC}"
echo "  1. Create Microsoft Advertising account"
echo "  2. Request developer token"
echo "  3. Register app in Azure AD"
echo "  4. Generate OAuth 2.0 access token"
echo ""

prompt_credential \
    "6. MICROSOFT ADS (Client ID)" \
    "MICROSOFT_CLIENT_ID" \
    "Microsoft/Azure AD Client ID" \
    "12345678-1234-1234-1234-123456789012"

prompt_credential \
    "6. MICROSOFT ADS (Client Secret)" \
    "MICROSOFT_CLIENT_SECRET" \
    "Microsoft Client Secret" \
    "abc123~DEF456..."

prompt_credential \
    "6. MICROSOFT ADS (Developer Token)" \
    "MICROSOFT_DEVELOPER_TOKEN" \
    "Bing Ads Developer Token" \
    "ABC123DEF456..."

prompt_credential \
    "6. MICROSOFT ADS (Customer ID)" \
    "MICROSOFT_CUSTOMER_ID" \
    "Microsoft Advertising Customer ID" \
    "123456789"

prompt_credential \
    "6. MICROSOFT ADS (Access Token)" \
    "MICROSOFT_ACCESS_TOKEN" \
    "Microsoft OAuth Access Token" \
    "eyJ0eXAiOiJKV1Q..."

# Summary
echo ""
echo "================================================================================"
echo " Configuration Complete!"
echo "================================================================================"
echo ""

# Count configured platforms
configured=0
[ -n "$(grep '^META_ACCESS_TOKEN=' "$ENV_FILE" | cut -d '=' -f2)" ] && ((configured++))
[ -n "$(grep '^GOOGLE_ADS_CREDENTIALS_PATH=' "$ENV_FILE" | cut -d '=' -f2)" ] && ((configured++))
[ -n "$(grep '^TIKTOK_ACCESS_TOKEN=' "$ENV_FILE" | cut -d '=' -f2)" ] && ((configured++))
[ -n "$(grep '^LINKEDIN_ACCESS_TOKEN=' "$ENV_FILE" | cut -d '=' -f2)" ] && ((configured++))
[ -n "$(grep '^AMAZON_ACCESS_TOKEN=' "$ENV_FILE" | cut -d '=' -f2)" ] && ((configured++))
[ -n "$(grep '^MICROSOFT_ACCESS_TOKEN=' "$ENV_FILE" | cut -d '=' -f2)" ] && ((configured++))

echo -e "${GREEN}Platforms Configured: $configured/6${NC}"
echo ""
echo "Configuration saved to: $ENV_FILE"
echo "Backup saved to:        $BACKUP_FILE"
echo ""
echo "Next Steps:"
echo "  1. Run migration: ./scripts/migrate_multi_platform.sh"
echo "  2. Test integration: cd app/services && python test_multi_platform.py"
echo "  3. Update stores table with platform account IDs"
echo "  4. Deploy to staging"
echo ""
echo -e "${YELLOW}Security Reminder:${NC}"
echo "  • Never commit .env file to git"
echo "  • Store production credentials in HashiCorp Vault"
echo "  • Rotate tokens every 60-90 days"
echo ""
