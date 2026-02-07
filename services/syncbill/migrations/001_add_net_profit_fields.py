"""
Database Migration: Add Net Profit Uplift Fields

Adds ad spend and net profit tracking fields to invoices table.

Run with:
    alembic revision --autogenerate -m "add_net_profit_fields"
    alembic upgrade head

Or manually:
    psql -U postgres -d syncbill -f migrations/add_net_profit_fields.sql
"""

# Alembic migration
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_net_profit_uplift'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add Net Profit Uplift fields to invoices table"""
    
    # Ad Spend Summary fields
    op.add_column('invoices', sa.Column('baseline_ad_spend', sa.Numeric(12, 2), nullable=False, server_default='0.0'))
    op.add_column('invoices', sa.Column('actual_ad_spend', sa.Numeric(12, 2), nullable=False, server_default='0.0'))
    op.add_column('invoices', sa.Column('incremental_ad_spend', sa.Numeric(12, 2), nullable=False, server_default='0.0'))
    op.add_column('invoices', sa.Column('ad_spend_uplift_percent', sa.Numeric(5, 2), server_default='0.0'))
    
    # Net Profit Calculation fields
    op.add_column('invoices', sa.Column('net_profit_uplift', sa.Numeric(12, 2), nullable=False, server_default='0.0'))
    op.add_column('invoices', sa.Column('baseline_profit', sa.Numeric(12, 2), server_default='0.0'))
    op.add_column('invoices', sa.Column('actual_profit', sa.Numeric(12, 2), server_default='0.0'))
    op.add_column('invoices', sa.Column('net_profit_uplift_percent', sa.Numeric(5, 2), server_default='0.0'))
    
    # Client Value fields
    op.add_column('invoices', sa.Column('client_net_gain', sa.Numeric(12, 2), server_default='0.0'))
    op.add_column('invoices', sa.Column('client_roi', sa.Numeric(5, 2), server_default='0.0'))
    
    print("✅ Added Net Profit Uplift fields to invoices table")


def downgrade():
    """Remove Net Profit Uplift fields from invoices table"""
    
    op.drop_column('invoices', 'client_roi')
    op.drop_column('invoices', 'client_net_gain')
    op.drop_column('invoices', 'net_profit_uplift_percent')
    op.drop_column('invoices', 'actual_profit')
    op.drop_column('invoices', 'baseline_profit')
    op.drop_column('invoices', 'net_profit_uplift')
    op.drop_column('invoices', 'ad_spend_uplift_percent')
    op.drop_column('invoices', 'incremental_ad_spend')
    op.drop_column('invoices', 'actual_ad_spend')
    op.drop_column('invoices', 'baseline_ad_spend')
    
    print("✅ Removed Net Profit Uplift fields from invoices table")


# SQL migration (alternative)
SQL_UPGRADE = """
-- Add Net Profit Uplift fields to invoices table
ALTER TABLE invoices 
ADD COLUMN baseline_ad_spend NUMERIC(12, 2) DEFAULT 0.0 NOT NULL,
ADD COLUMN actual_ad_spend NUMERIC(12, 2) DEFAULT 0.0 NOT NULL,
ADD COLUMN incremental_ad_spend NUMERIC(12, 2) DEFAULT 0.0 NOT NULL,
ADD COLUMN ad_spend_uplift_percent NUMERIC(5, 2) DEFAULT 0.0,
ADD COLUMN net_profit_uplift NUMERIC(12, 2) DEFAULT 0.0 NOT NULL,
ADD COLUMN baseline_profit NUMERIC(12, 2) DEFAULT 0.0,
ADD COLUMN actual_profit NUMERIC(12, 2) DEFAULT 0.0,
ADD COLUMN net_profit_uplift_percent NUMERIC(5, 2) DEFAULT 0.0,
ADD COLUMN client_net_gain NUMERIC(12, 2) DEFAULT 0.0,
ADD COLUMN client_roi NUMERIC(5, 2) DEFAULT 0.0;

-- Update existing invoices to calculate Net Profit fields
UPDATE invoices
SET 
    baseline_profit = baseline_revenue - baseline_ad_spend,
    actual_profit = actual_revenue - actual_ad_spend,
    net_profit_uplift = incremental_revenue - incremental_ad_spend,
    client_net_gain = (incremental_revenue - incremental_ad_spend) - subtotal,
    client_roi = CASE 
        WHEN subtotal > 0 THEN ((incremental_revenue - incremental_ad_spend) - subtotal) / subtotal
        ELSE 0
    END
WHERE baseline_ad_spend > 0 OR actual_ad_spend > 0;

COMMIT;
"""

SQL_DOWNGRADE = """
-- Remove Net Profit Uplift fields from invoices table
ALTER TABLE invoices 
DROP COLUMN client_roi,
DROP COLUMN client_net_gain,
DROP COLUMN net_profit_uplift_percent,
DROP COLUMN actual_profit,
DROP COLUMN baseline_profit,
DROP COLUMN net_profit_uplift,
DROP COLUMN ad_spend_uplift_percent,
DROP COLUMN incremental_ad_spend,
DROP COLUMN actual_ad_spend,
DROP COLUMN baseline_ad_spend;

COMMIT;
"""


if __name__ == "__main__":
    # For manual testing
    print("Net Profit Uplift Migration")
    print("=" * 60)
    print("\nUPGRADE SQL:")
    print(SQL_UPGRADE)
    print("\nDOWNGRADE SQL:")
    print(SQL_DOWNGRADE)
