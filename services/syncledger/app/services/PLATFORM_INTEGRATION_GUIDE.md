# Multi-Platform Ad Spend Integration Guide

## Quick Start

### Step 1: Install Dependencies

```bash
# Already installed
pip install stripe facebook-business google-ads

# NEW: Install for additional platforms
pip install httpx  # Already installed (for TikTok, LinkedIn, Amazon)
pip install bingads  # Microsoft Advertising SDK
```

### Step 2: Update Configuration

Add to `services/syncledger/app/config.py`:

```python
# Existing (already configured)
meta_app_id: str = os.getenv("META_APP_ID")
meta_app_secret: str = os.getenv("META_APP_SECRET")
meta_access_token: str = os.getenv("META_ACCESS_TOKEN")
google_ads_credentials_path: str = os.getenv("GOOGLE_ADS_CREDENTIALS_PATH")

# NEW: TikTok Ads
tiktok_app_id: str = os.getenv("TIKTOK_APP_ID")
tiktok_app_secret: str = os.getenv("TIKTOK_APP_SECRET")
tiktok_access_token: str = os.getenv("TIKTOK_ACCESS_TOKEN")

# NEW: LinkedIn Ads
linkedin_client_id: str = os.getenv("LINKEDIN_CLIENT_ID")
linkedin_client_secret: str = os.getenv("LINKEDIN_CLIENT_SECRET")
linkedin_access_token: str = os.getenv("LINKEDIN_ACCESS_TOKEN")

# NEW: Amazon Advertising
amazon_client_id: str = os.getenv("AMAZON_CLIENT_ID")
amazon_client_secret: str = os.getenv("AMAZON_CLIENT_SECRET")
amazon_access_token: str = os.getenv("AMAZON_ACCESS_TOKEN")
amazon_refresh_token: str = os.getenv("AMAZON_REFRESH_TOKEN")

# NEW: Microsoft Advertising
microsoft_client_id: str = os.getenv("MICROSOFT_CLIENT_ID")
microsoft_client_secret: str = os.getenv("MICROSOFT_CLIENT_SECRET")
microsoft_developer_token: str = os.getenv("MICROSOFT_DEVELOPER_TOKEN")
microsoft_customer_id: str = os.getenv("MICROSOFT_CUSTOMER_ID")
microsoft_access_token: str = os.getenv("MICROSOFT_ACCESS_TOKEN")
```

### Step 3: Update Environment Variables

Edit `.env` file:

```bash
# EXISTING - Meta Ads
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
META_ACCESS_TOKEN=your_meta_access_token

# EXISTING - Google Ads
GOOGLE_ADS_CREDENTIALS_PATH=/path/to/google-ads.yaml

# NEW - TikTok Ads
TIKTOK_APP_ID=your_tiktok_app_id
TIKTOK_APP_SECRET=your_tiktok_app_secret
TIKTOK_ACCESS_TOKEN=your_tiktok_access_token

# NEW - LinkedIn Ads
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

# NEW - Amazon Advertising
AMAZON_CLIENT_ID=amzn1.application-oa2-client.xxx
AMAZON_CLIENT_SECRET=your_amazon_secret
AMAZON_ACCESS_TOKEN=Atza|xxx
AMAZON_REFRESH_TOKEN=Atzr|xxx

# NEW - Microsoft Advertising
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
MICROSOFT_DEVELOPER_TOKEN=your_microsoft_dev_token
MICROSOFT_CUSTOMER_ID=your_microsoft_customer_id
MICROSOFT_ACCESS_TOKEN=your_microsoft_access_token
```

### Step 4: Database Migration

Add platform-specific account ID columns:

```sql
-- Migration: Add multi-platform ad account tracking
ALTER TABLE stores
ADD COLUMN tiktok_advertiser_id VARCHAR(100),
ADD COLUMN linkedin_account_urn VARCHAR(255),
ADD COLUMN amazon_profile_id VARCHAR(100),
ADD COLUMN microsoft_account_id VARCHAR(100),
ADD COLUMN snapchat_org_id VARCHAR(100),
ADD COLUMN pinterest_ad_account_id VARCHAR(100);

-- Index for faster lookups
CREATE INDEX idx_stores_tiktok ON stores(tiktok_advertiser_id);
CREATE INDEX idx_stores_linkedin ON stores(linkedin_account_urn);
CREATE INDEX idx_stores_amazon ON stores(amazon_profile_id);
CREATE INDEX idx_stores_microsoft ON stores(microsoft_account_id);

-- Update baseline_snapshots table to track per-platform spend
ALTER TABLE baseline_snapshots
ADD COLUMN tiktok_spend DECIMAL(12, 2) DEFAULT 0.00,
ADD COLUMN linkedin_spend DECIMAL(12, 2) DEFAULT 0.00,
ADD COLUMN amazon_spend DECIMAL(12, 2) DEFAULT 0.00,
ADD COLUMN microsoft_spend DECIMAL(12, 2) DEFAULT 0.00;

-- Update ledger_entries table for per-platform attribution
ALTER TABLE ledger_entries
ADD COLUMN platform VARCHAR(50) DEFAULT 'unknown',
ADD COLUMN platform_campaign_id VARCHAR(100);

CREATE INDEX idx_ledger_platform ON ledger_entries(platform);
```

### Step 5: Switch to Extended Fetcher

Update imports in `services/syncledger/app/handlers.go` (or equivalent):

**Before**:
```python
from app.services.ad_spend_fetcher import AdSpendFetcher
```

**After**:
```python
from app.services.ad_spend_fetcher_extended import AdSpendFetcherExtended as AdSpendFetcher
```

Or rename the file:
```bash
cd services/syncledger/app/services
mv ad_spend_fetcher.py ad_spend_fetcher_legacy.py
mv ad_spend_fetcher_extended.py ad_spend_fetcher.py
```

### Step 6: Test Integration

```python
# tests/test_multi_platform.py
import pytest
from app.services.ad_spend_fetcher import AdSpendFetcher
from datetime import datetime, timedelta
from decimal import Decimal

@pytest.mark.asyncio
async def test_all_platforms():
    fetcher = AdSpendFetcher()
    
    ad_accounts = {
        "meta_account_id": "123456789",
        "google_customer_id": "123-456-7890",
        "tiktok_advertiser_id": "7123456789012345",
        "linkedin_account_urn": "urn:li:sponsoredAccount:123456",
        "amazon_profile_id": "1234567890123",
        "microsoft_account_id": "123456789"
    }
    
    end = datetime.now()
    start = end - timedelta(days=30)
    
    result = await fetcher.get_total_spend_for_period(
        store_id=1,
        start_date=start,
        end_date=end,
        ad_accounts=ad_accounts
    )
    
    # Verify all platforms present
    assert "meta_spend" in result
    assert "google_spend" in result
    assert "tiktok_spend" in result
    assert "linkedin_spend" in result
    assert "amazon_spend" in result
    assert "microsoft_spend" in result
    assert "total_spend" in result
    
    # Verify total = sum
    expected = (
        result["meta_spend"] +
        result["google_spend"] +
        result["tiktok_spend"] +
        result["linkedin_spend"] +
        result["amazon_spend"] +
        result["microsoft_spend"]
    )
    assert result["total_spend"] == expected
    
    print(f"✅ Total spend: ${result['total_spend']:.2f}")
    for platform in ["meta", "google", "tiktok", "linkedin", "amazon", "microsoft"]:
        print(f"   {platform.capitalize()}: ${result[f'{platform}_spend']:.2f}")
```

Run tests:
```bash
cd services/syncledger
pytest tests/test_multi_platform.py -v
```

---

## Platform-Specific Setup Guides

### 🎵 TikTok Ads

1. **Create TikTok for Business account**: https://ads.tiktok.com/
2. **Register app**: https://ads.tiktok.com/marketing_api/apps
3. **Get credentials**:
   - App ID
   - App Secret
   - Access Token (OAuth 2.0)
4. **Permissions required**:
   - `advertiser.read`
   - `advertiser.data.read`
   - `reporting.read`
5. **Rate limits**: 10 requests/minute per advertiser

**Testing**:
```python
fetcher = AdSpendFetcher()
spend = await fetcher.get_tiktok_spend(
    advertiser_id="7123456789012345",
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31)
)
print(f"TikTok spend: ${spend:.2f}")
```

---

### 💼 LinkedIn Ads

1. **Create LinkedIn Campaign Manager account**: https://business.linkedin.com/marketing-solutions
2. **Create app**: https://www.linkedin.com/developers/apps
3. **Get credentials**:
   - Client ID
   - Client Secret
   - Access Token (OAuth 2.0, scopes: `r_ads`, `rw_ads`)
4. **Rate limits**: 100 requests/minute per user

**Testing**:
```python
spend = await fetcher.get_linkedin_spend(
    account_id="urn:li:sponsoredAccount:123456",
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31)
)
print(f"LinkedIn spend: ${spend:.2f}")
```

---

### 📦 Amazon Advertising

1. **Create Amazon Advertising account**: https://advertising.amazon.com/
2. **Register for API access**: https://advertising.amazon.com/API
3. **Get credentials**:
   - Client ID (amzn1.application-oa2-client.xxx)
   - Client Secret
   - Access Token (Login with Amazon OAuth)
   - Refresh Token
4. **Rate limits**: 100 requests/minute
5. **Note**: Report generation is asynchronous (30-60 second delay)

**Testing**:
```python
spend = await fetcher.get_amazon_spend(
    profile_id="1234567890123",
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31)
)
print(f"Amazon spend: ${spend:.2f}")
```

---

### 🔍 Microsoft Advertising (Bing)

1. **Create Microsoft Advertising account**: https://ads.microsoft.com/
2. **Request API access**: https://learn.microsoft.com/en-us/advertising/guides/get-started
3. **Get credentials**:
   - Client ID
   - Client Secret
   - Developer Token
   - Customer ID
   - Access Token (OAuth 2.0)
4. **Install SDK**: `pip install bingads`
5. **Rate limits**: Varies by operation

**Testing**:
```python
spend = await fetcher.get_microsoft_spend(
    account_id="123456789",
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31)
)
print(f"Microsoft spend: ${spend:.2f}")
```

---

## Production Deployment Checklist

### Pre-Launch
- [ ] All platform credentials stored in HashiCorp Vault
- [ ] Database migrations executed in staging
- [ ] API rate limiting configured (avoid hitting platform limits)
- [ ] Token refresh logic implemented (tokens expire)
- [ ] Error logging configured (send to SyncShield audit logs)
- [ ] Prometheus metrics added (`kiki_ad_spend_fetch_errors_total{platform="tiktok"}`)

### Testing
- [ ] Unit tests pass for all 6 platforms
- [ ] Integration tests with live API credentials (staging accounts)
- [ ] Load testing (concurrent fetches from 100+ stores)
- [ ] Failover testing (what happens if TikTok API is down?)

### Monitoring
- [ ] Grafana dashboard shows spend by platform
- [ ] Alerts configured for:
  - API errors >5% per platform
  - Missing spend data for >1 hour
  - Token expiration warnings
- [ ] Daily summary reports to operations team

### Documentation
- [ ] Client onboarding guide updated (how to connect TikTok, LinkedIn, etc.)
- [ ] API documentation updated (`/docs/API_REFERENCE.md`)
- [ ] Support team training on troubleshooting platform integrations

---

## Troubleshooting

### TikTok API returns "code": 40001
**Issue**: Invalid access token  
**Fix**: Refresh OAuth token at https://ads.tiktok.com/marketing_api/auth

### LinkedIn returns 401 Unauthorized
**Issue**: Access token expired (expires every 60 days)  
**Fix**: Re-authenticate and update `LINKEDIN_ACCESS_TOKEN` in `.env`

### Amazon report stuck in "IN_PROGRESS" status
**Issue**: Amazon Ads API is slow (can take 60+ seconds)  
**Fix**: Increase timeout to 120 seconds in `get_amazon_spend()`:
```python
for attempt in range(24):  # 24 * 5s = 120s max
    await asyncio.sleep(5)
    ...
```

### Microsoft Ads SDK throws SSL error
**Issue**: Certificate validation failure  
**Fix**: Update `bingads` package:
```bash
pip install --upgrade bingads
```

---

## FAQ

**Q: Do we need to implement all 6 platforms at once?**  
A: No. Start with TikTok + LinkedIn (highest ROI). Add others as client demand grows.

**Q: What happens if a client only uses Meta + Google?**  
A: The fetcher will gracefully skip platforms with missing credentials (returns `Decimal("0.00")`).

**Q: Can we add Snapchat, Pinterest, Reddit later?**  
A: Yes. Follow the same pattern:
1. Add `get_snapchat_spend()` method
2. Update `get_total_spend_for_period()` to include Snapchat
3. Add database columns for `snapchat_org_id`

**Q: How do we handle currency conversion (EUR, GBP, etc.)?**  
A: All platforms return spend in USD by default. For non-USD accounts, add currency conversion in Phase 2.

**Q: What's the expected performance impact?**  
A: Fetching from 6 platforms concurrently takes ~5-10 seconds (limited by slowest platform, typically Amazon).

---

## Next Steps

1. **Week 1-2**: Implement TikTok + LinkedIn
2. **Week 3-4**: Add Amazon + Microsoft
3. **Week 5**: Production deployment with monitoring
4. **Week 6+**: Add remaining platforms (Snapchat, Pinterest) based on demand

---

*Last Updated: February 7, 2026*  
*Maintainer: KIKI Revenue Engineering Team*
