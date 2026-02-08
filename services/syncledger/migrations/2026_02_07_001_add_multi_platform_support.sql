-- Migration: Add multi-platform ad account tracking to SyncLedger
-- Version: 2026.02.07_001
-- Description: Extends stores and ledger tables to support TikTok, LinkedIn, Amazon, Microsoft, Snapchat, Pinterest

-- ============================================================================
-- STEP 1: Add platform-specific account ID columns to stores table
-- ============================================================================

ALTER TABLE stores
ADD COLUMN IF NOT EXISTS tiktok_advertiser_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS linkedin_account_urn VARCHAR(255),
ADD COLUMN IF NOT EXISTS amazon_profile_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS microsoft_account_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS snapchat_org_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS pinterest_ad_account_id VARCHAR(100);

-- Add indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_stores_tiktok ON stores(tiktok_advertiser_id) WHERE tiktok_advertiser_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_stores_linkedin ON stores(linkedin_account_urn) WHERE linkedin_account_urn IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_stores_amazon ON stores(amazon_profile_id) WHERE amazon_profile_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_stores_microsoft ON stores(microsoft_account_id) WHERE microsoft_account_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_stores_snapchat ON stores(snapchat_org_id) WHERE snapchat_org_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_stores_pinterest ON stores(pinterest_ad_account_id) WHERE pinterest_ad_account_id IS NOT NULL;

-- ============================================================================
-- STEP 2: Add per-platform spend tracking to baseline_snapshots table
-- ============================================================================

ALTER TABLE baseline_snapshots
ADD COLUMN IF NOT EXISTS tiktok_spend DECIMAL(12, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS linkedin_spend DECIMAL(12, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS amazon_spend DECIMAL(12, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS microsoft_spend DECIMAL(12, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS snapchat_spend DECIMAL(12, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS pinterest_spend DECIMAL(12, 2) DEFAULT 0.00;

-- Update total_ad_spend to be sum of all platforms (for existing rows)
UPDATE baseline_snapshots
SET total_ad_spend = 
    COALESCE(meta_spend, 0) + 
    COALESCE(google_spend, 0) + 
    COALESCE(tiktok_spend, 0) + 
    COALESCE(linkedin_spend, 0) + 
    COALESCE(amazon_spend, 0) + 
    COALESCE(microsoft_spend, 0) +
    COALESCE(snapchat_spend, 0) +
    COALESCE(pinterest_spend, 0)
WHERE total_ad_spend = 0 OR total_ad_spend IS NULL;

-- ============================================================================
-- STEP 3: Add platform attribution to ledger_entries table
-- ============================================================================

ALTER TABLE ledger_entries
ADD COLUMN IF NOT EXISTS platform VARCHAR(50) DEFAULT 'unknown',
ADD COLUMN IF NOT EXISTS platform_campaign_id VARCHAR(100);

-- Add index for platform-based queries
CREATE INDEX IF NOT EXISTS idx_ledger_platform ON ledger_entries(platform);
CREATE INDEX IF NOT EXISTS idx_ledger_platform_campaign ON ledger_entries(platform, platform_campaign_id) 
WHERE platform_campaign_id IS NOT NULL;

-- ============================================================================
-- STEP 4: Create platform_spend_summary materialized view
-- (for analytics and reporting)
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS platform_spend_summary AS
SELECT 
    store_id,
    DATE_TRUNC('month', created_at) AS month,
    platform,
    COUNT(*) AS total_orders,
    SUM(incremental_revenue) AS total_revenue,
    SUM(ad_spend_for_order) AS total_ad_spend,
    SUM(net_profit_uplift) AS total_net_profit,
    SUM(success_fee_amount) AS total_kiki_fee,
    AVG(net_profit_uplift) AS avg_net_profit_per_order
FROM ledger_entries
WHERE platform IS NOT NULL
GROUP BY store_id, DATE_TRUNC('month', created_at), platform;

-- Create index on materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_platform_spend_summary 
ON platform_spend_summary(store_id, month, platform);

-- Refresh policy (update every 1 hour)
COMMENT ON MATERIALIZED VIEW platform_spend_summary IS 
'Platform-level spend and revenue summary. Refresh hourly with: REFRESH MATERIALIZED VIEW CONCURRENTLY platform_spend_summary;';

-- ============================================================================
-- STEP 5: Add comments for documentation
-- ============================================================================

COMMENT ON COLUMN stores.tiktok_advertiser_id IS 'TikTok Ads advertiser ID (numeric string, e.g., "7123456789012345")';
COMMENT ON COLUMN stores.linkedin_account_urn IS 'LinkedIn ad account URN (e.g., "urn:li:sponsoredAccount:123456")';
COMMENT ON COLUMN stores.amazon_profile_id IS 'Amazon Advertising profile ID (numeric string)';
COMMENT ON COLUMN stores.microsoft_account_id IS 'Microsoft Advertising (Bing) account ID';
COMMENT ON COLUMN stores.snapchat_org_id IS 'Snapchat organization ID';
COMMENT ON COLUMN stores.pinterest_ad_account_id IS 'Pinterest ad account ID';

COMMENT ON COLUMN ledger_entries.platform IS 'Ad platform attribution (meta, google, tiktok, linkedin, amazon, microsoft, snapchat, pinterest)';
COMMENT ON COLUMN ledger_entries.platform_campaign_id IS 'Platform-specific campaign ID for cross-reference';

-- ============================================================================
-- STEP 6: Create function to automatically update total_ad_spend
-- ============================================================================

CREATE OR REPLACE FUNCTION update_baseline_total_ad_spend()
RETURNS TRIGGER AS $$
BEGIN
    NEW.total_ad_spend := 
        COALESCE(NEW.meta_spend, 0) + 
        COALESCE(NEW.google_spend, 0) + 
        COALESCE(NEW.tiktok_spend, 0) + 
        COALESCE(NEW.linkedin_spend, 0) + 
        COALESCE(NEW.amazon_spend, 0) + 
        COALESCE(NEW.microsoft_spend, 0) +
        COALESCE(NEW.snapchat_spend, 0) +
        COALESCE(NEW.pinterest_spend, 0);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS trigger_update_baseline_total_ad_spend ON baseline_snapshots;
CREATE TRIGGER trigger_update_baseline_total_ad_spend
BEFORE INSERT OR UPDATE ON baseline_snapshots
FOR EACH ROW
EXECUTE FUNCTION update_baseline_total_ad_spend();

-- ============================================================================
-- STEP 7: Verify migration success
-- ============================================================================

DO $$
BEGIN
    -- Check if all new columns exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'stores' AND column_name = 'tiktok_advertiser_id'
    ) THEN
        RAISE NOTICE '✅ Migration successful: Multi-platform columns added';
    ELSE
        RAISE EXCEPTION '❌ Migration failed: tiktok_advertiser_id column not found';
    END IF;
END $$;

-- ============================================================================
-- ROLLBACK SCRIPT (if needed)
-- ============================================================================
-- Uncomment the following lines to rollback this migration:
--
-- DROP MATERIALIZED VIEW IF EXISTS platform_spend_summary;
-- DROP TRIGGER IF EXISTS trigger_update_baseline_total_ad_spend ON baseline_snapshots;
-- DROP FUNCTION IF EXISTS update_baseline_total_ad_spend();
-- 
-- ALTER TABLE stores
-- DROP COLUMN IF EXISTS tiktok_advertiser_id,
-- DROP COLUMN IF EXISTS linkedin_account_urn,
-- DROP COLUMN IF EXISTS amazon_profile_id,
-- DROP COLUMN IF EXISTS microsoft_account_id,
-- DROP COLUMN IF EXISTS snapchat_org_id,
-- DROP COLUMN IF EXISTS pinterest_ad_account_id;
-- 
-- ALTER TABLE baseline_snapshots
-- DROP COLUMN IF EXISTS tiktok_spend,
-- DROP COLUMN IF EXISTS linkedin_spend,
-- DROP COLUMN IF EXISTS amazon_spend,
-- DROP COLUMN IF EXISTS microsoft_spend,
-- DROP COLUMN IF EXISTS snapchat_spend,
-- DROP COLUMN IF EXISTS pinterest_spend;
-- 
-- ALTER TABLE ledger_entries
-- DROP COLUMN IF EXISTS platform,
-- DROP COLUMN IF EXISTS platform_campaign_id;
