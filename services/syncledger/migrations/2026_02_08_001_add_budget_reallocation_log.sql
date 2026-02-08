-- Migration: Add budget_reallocation_log table for GlobalBudgetOptimizer
-- Created: 2026-02-08
-- Purpose: Track cross-platform budget shifts for OaaS attribution and audit trail
--
-- This table logs every automated budget reallocation decision made by the
-- GlobalBudgetOptimizer in SyncFlow. Each entry records:
-- - Which platforms were involved (from_platform → to_platform)
-- - How much budget was shifted (amount_shifted)
-- - Why the shift occurred (reason with efficiency metrics)
-- - When it happened (timestamp + created_at)
--
-- Used by:
-- - SyncFlow GlobalBudgetOptimizer (logs shifts every 5 minutes)
-- - SyncBill (attributes Net Profit Uplift per platform)
-- - Grafana Dashboard (Budget Reallocation Timeline panel)
-- - Compliance/Audit (immutable log of algorithmic decisions)

CREATE TABLE IF NOT EXISTS budget_reallocation_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  
  -- Client identification
  client_id VARCHAR(255) NOT NULL,
  
  -- Platform shift details
  from_platform VARCHAR(50) NOT NULL,
  to_platform VARCHAR(50) NOT NULL,
  amount_shifted DECIMAL(10,2) NOT NULL,
  
  -- Efficiency metrics (LTV-to-CAC ratios)
  from_efficiency DECIMAL(5,2) DEFAULT NULL,
  to_efficiency DECIMAL(5,2) DEFAULT NULL,
  
  -- Decision explanation (XAI compliance)
  reason TEXT NOT NULL,
  
  -- Timestamps
  timestamp BIGINT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  -- Indexes for performance
  INDEX idx_client_timestamp (client_id, timestamp),
  INDEX idx_platforms (from_platform, to_platform),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add audit comment for SOC2/GDPR compliance
ALTER TABLE budget_reallocation_log COMMENT = 
  'Immutable audit log of automated budget reallocations by GlobalBudgetOptimizer. '
  'Used for OaaS revenue attribution and algorithmic transparency.';

-- Example query: Last 10 budget shifts for a client
-- SELECT from_platform, to_platform, amount_shifted, from_efficiency, to_efficiency, reason, 
--        FROM_UNIXTIME(timestamp) as shift_time
-- FROM budget_reallocation_log
-- WHERE client_id = 'demo-client-001'
-- ORDER BY timestamp DESC
-- LIMIT 10;
