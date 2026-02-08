#!/bin/bash
# Master Deployment Script for Multi-Platform Integration
# Orchestrates the entire deployment process

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "================================================================================"
echo " KIKI Agent™ - Multi-Platform Integration Deployment"
echo "================================================================================"
echo ""
echo "This script will:"
echo "  1. Install Python dependencies"
echo "  2. Set up API credentials (interactive)"
echo "  3. Run database migration"
echo "  4. Run integration tests"
echo "  5. Display next steps"
echo ""

read -p "Continue with deployment? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled"
    exit 0
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}STEP 1: Installing Python Dependencies${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd /workspaces/kiki-agent-syncshield/services/syncledger/app/services
pip install -q -r requirements.txt
pip install -q pydantic-settings

echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

read -p "Skip credential setup? (yes/no): " skip_creds
if [ "$skip_creds" != "yes" ]; then
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}STEP 2: Setting Up API Credentials${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    /workspaces/kiki-agent-syncshield/services/syncledger/scripts/setup_credentials.sh
else
    echo ""
    echo -e "${YELLOW}⏭️  Skipping credential setup${NC}"
fi

echo ""
read -p "Run database migration? (yes/no): " run_migration
if [ "$run_migration" = "yes" ]; then
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}STEP 3: Running Database Migration${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    /workspaces/kiki-agent-syncshield/services/syncledger/scripts/migrate_multi_platform.sh
else
    echo ""
    echo -e "${YELLOW}⏭️  Skipping database migration${NC}"
fi

echo ""
read -p "Run integration tests? (yes/no): " run_tests
if [ "$run_tests" = "yes" ]; then
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}STEP 4: Running Integration Tests${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    cd /workspaces/kiki-agent-syncshield/services/syncledger/app/services
    python test_multi_platform.py
else
    echo ""
    echo -e "${YELLOW}⏭️  Skipping integration tests${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}DEPLOYMENT COMPLETE!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Next Steps:"
echo ""
echo "1. Update stores table with platform account IDs:"
echo "   psql -U postgres -d kiki_ledger"
echo "   UPDATE stores SET"
echo "     tiktok_advertiser_id = '7123456789012345',"
echo "     linkedin_account_urn = 'urn:li:sponsoredAccount:123456'"
echo "   WHERE id = 1;"
echo ""
echo "2. Import Grafana dashboard:"
echo "   Dashboard file: /workspaces/kiki-agent-syncshield/deploy/grafana/dashboards/multi_platform_ad_spend.json"
echo "   Go to Grafana UI → Dashboards → Import → Upload JSON"
echo ""
echo "3. Deploy to staging:"
echo "   cd /workspaces/kiki-agent-syncshield/services/syncledger"
echo "   go build -o syncledger"
echo "   docker-compose up --build syncledger"
echo ""
echo "4. Monitor metrics:"
echo "   Grafana: http://localhost:3000/d/multi-platform-ad-spend"
echo "   Prometheus: http://localhost:9090/graph"
echo ""
echo "Documentation:"
echo "  • Deployment Guide: services/syncledger/app/services/DEPLOYMENT_SUMMARY.md"
echo "  • Integration Guide: services/syncledger/app/services/PLATFORM_INTEGRATION_GUIDE.md"
echo "  • Expansion Roadmap: services/syncledger/app/services/MULTI_PLATFORM_EXPANSION.md"
echo ""
echo -e "${GREEN}🎉 Multi-platform integration is ready!${NC}"
echo ""
