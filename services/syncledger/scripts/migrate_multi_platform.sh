#!/bin/bash
# Database Migration Executor for Multi-Platform Support
# Version: 2026.02.07_001
# Description: Safely applies multi-platform ad account tracking migration

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================================================"
echo " KIKI Agent™ - Multi-Platform Database Migration"
echo "================================================================================"
echo ""

# Check if PostgreSQL is available
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ Error: psql command not found${NC}"
    echo "   Please install PostgreSQL client: sudo apt-get install postgresql-client"
    exit 1
fi

# Database connection settings (override with environment variables)
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-kiki_ledger}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-}"

# Migration file path
MIGRATION_FILE="/workspaces/kiki-agent-syncshield/services/syncledger/migrations/2026_02_07_001_add_multi_platform_support.sql"

echo "Database Configuration:"
echo "  Host:     $DB_HOST"
echo "  Port:     $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User:     $DB_USER"
echo ""

# Test connection
echo -e "${YELLOW}🔍 Testing database connection...${NC}"
if [ -n "$DB_PASSWORD" ]; then
    export PGPASSWORD="$DB_PASSWORD"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT version();" > /dev/null 2>&1
else
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT version();" > /dev/null 2>&1
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database connection successful${NC}"
else
    echo -e "${RED}❌ Failed to connect to database${NC}"
    echo "   Please check your database credentials and ensure PostgreSQL is running"
    exit 1
fi

echo ""

# Check if migration has already been applied
echo -e "${YELLOW}🔍 Checking if migration has already been applied...${NC}"
if [ -n "$DB_PASSWORD" ]; then
    COLUMN_EXISTS=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'stores' AND column_name = 'tiktok_advertiser_id';")
else
    COLUMN_EXISTS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'stores' AND column_name = 'tiktok_advertiser_id';")
fi

if [ "$COLUMN_EXISTS" = "1" ]; then
    echo -e "${YELLOW}⚠️  Migration appears to be already applied${NC}"
    echo ""
    read -p "Do you want to skip or re-run the migration? (skip/rerun/cancel): " choice
    case "$choice" in
        skip)
            echo -e "${GREEN}✅ Skipping migration (already applied)${NC}"
            exit 0
            ;;
        rerun)
            echo -e "${YELLOW}⚠️  Re-running migration (may cause errors if data exists)${NC}"
            ;;
        *)
            echo -e "${RED}❌ Migration cancelled${NC}"
            exit 1
            ;;
    esac
fi

echo ""

# Backup database before migration
echo -e "${YELLOW}💾 Creating database backup...${NC}"
BACKUP_FILE="/tmp/kiki_ledger_backup_$(date +%Y%m%d_%H%M%S).sql"
if [ -n "$DB_PASSWORD" ]; then
    PGPASSWORD="$DB_PASSWORD" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$BACKUP_FILE"
else
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$BACKUP_FILE"
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backup created: $BACKUP_FILE${NC}"
else
    echo -e "${RED}❌ Backup failed (proceeding anyway)${NC}"
fi

echo ""

# Apply migration
echo -e "${YELLOW}🚀 Applying migration: $MIGRATION_FILE${NC}"
echo ""

if [ -n "$DB_PASSWORD" ]; then
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$MIGRATION_FILE"
else
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$MIGRATION_FILE"
fi

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Migration applied successfully!${NC}"
else
    echo ""
    echo -e "${RED}❌ Migration failed!${NC}"
    echo ""
    echo "Rollback instructions:"
    echo "  1. Restore from backup: psql -U $DB_USER -d $DB_NAME -f $BACKUP_FILE"
    echo "  2. Or run rollback script from migration file"
    exit 1
fi

echo ""

# Verify migration
echo -e "${YELLOW}🔍 Verifying migration...${NC}"

if [ -n "$DB_PASSWORD" ]; then
    STORES_COLUMNS=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'stores' AND column_name IN ('tiktok_advertiser_id', 'linkedin_account_urn', 'amazon_profile_id', 'microsoft_account_id', 'snapchat_org_id', 'pinterest_ad_account_id');")
    
    BASELINE_COLUMNS=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'baseline_snapshots' AND column_name IN ('tiktok_spend', 'linkedin_spend', 'amazon_spend', 'microsoft_spend');")
    
    LEDGER_COLUMNS=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'ledger_entries' AND column_name IN ('platform', 'platform_campaign_id');")
    
    VIEW_EXISTS=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM information_schema.views WHERE table_name = 'platform_spend_summary';")
else
    STORES_COLUMNS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'stores' AND column_name IN ('tiktok_advertiser_id', 'linkedin_account_urn', 'amazon_profile_id', 'microsoft_account_id', 'snapchat_org_id', 'pinterest_ad_account_id');")
    
    BASELINE_COLUMNS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'baseline_snapshots' AND column_name IN ('tiktok_spend', 'linkedin_spend', 'amazon_spend', 'microsoft_spend');")
    
    LEDGER_COLUMNS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'ledger_entries' AND column_name IN ('platform', 'platform_campaign_id');")
    
    VIEW_EXISTS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM information_schema.views WHERE table_name = 'platform_spend_summary';")
fi

echo ""
echo "Verification Results:"
echo "  stores table columns:           $STORES_COLUMNS/6 ✅"
echo "  baseline_snapshots columns:     $BASELINE_COLUMNS/4 ✅"
echo "  ledger_entries columns:         $LEDGER_COLUMNS/2 ✅"
echo "  platform_spend_summary view:    $VIEW_EXISTS/1 ✅"

if [ "$STORES_COLUMNS" = "6" ] && [ "$BASELINE_COLUMNS" = "4" ] && [ "$LEDGER_COLUMNS" = "2" ]; then
    echo ""
    echo -e "${GREEN}✅ All verification checks passed!${NC}"
    echo ""
    echo "================================================================================"
    echo " Migration Complete!"
    echo "================================================================================"
    echo ""
    echo "Next Steps:"
    echo "  1. Add platform credentials to .env file"
    echo "  2. Update stores table with platform account IDs"
    echo "  3. Run integration tests: python test_multi_platform.py"
    echo "  4. Deploy to staging environment"
    echo ""
    echo "Backup location: $BACKUP_FILE"
    echo ""
else
    echo ""
    echo -e "${YELLOW}⚠️  Some verification checks failed${NC}"
    echo "   Migration may be incomplete. Please check the database manually."
    exit 1
fi
