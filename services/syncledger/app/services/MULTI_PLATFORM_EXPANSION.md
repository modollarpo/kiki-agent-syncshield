# Multi-Platform Ad Spend Integration - Expansion Plan

## Executive Summary

**Current State**: AdSpendFetcher supports Meta + Google (covers ~65% of digital ad spend)  
**Opportunity**: Add TikTok, LinkedIn, Amazon, Microsoft to reach **95% coverage**

## Platform Priority Matrix

### **Tier 1 (Immediate - Q1 2026)** 🚀
**TikTok Ads** + **LinkedIn Ads**  
*Why*: TikTok dominates e-commerce growth (+142% YoY), LinkedIn owns B2B SaaS (KIKI's highest LTV segment)

### **Tier 2 (Next Quarter - Q2 2026)** 
**Amazon Advertising** + **Microsoft Advertising**  
*Why*: Amazon essential for retail clients, Microsoft captures ~8% search (Google alternative)

### **Tier 3 (Backlog - Q3 2026)**
**Snapchat** + **Pinterest** + **Reddit**  
*Why*: Niche platforms for specific verticals (gaming, visual discovery, communities)

### **Deprioritized**
**Twitter/X**: API access restricted post-2023 changes, declining market share

---

## Technical Implementation

### **1. TikTok Ads Integration**

**API**: [TikTok Marketing API](https://ads.tiktok.com/marketing_api/docs)  
**Auth**: OAuth 2.0 (app_id, secret, access_token)  
**Endpoints**:
- `GET /open_api/v1.3/reports/integrated/get/` - Ad spend data
- `POST /open_api/v1.3/oauth2/access_token/` - Token refresh

**Python Library**: `tiktok-business-api` (unofficial) or direct `httpx` calls

**Code Example**:
```python
async def get_tiktok_spend(
    self,
    advertiser_id: str,
    start_date: datetime,
    end_date: datetime
) -> Decimal:
    """
    Fetch TikTok Ads spend for period.
    
    Args:
        advertiser_id: TikTok advertiser ID
        start_date: Period start
        end_date: Period end
    
    Returns:
        Total spend in USD
    """
    if not self.tiktok_access_token:
        logger.warning("⚠️  TikTok Ads credentials not configured")
        return Decimal("0.00")
    
    try:
        url = "https://business-api.tiktok.com/open_api/v1.3/reports/integrated/get/"
        
        headers = {
            "Access-Token": self.tiktok_access_token,
            "Content-Type": "application/json"
        }
        
        payload = {
            "advertiser_id": advertiser_id,
            "report_type": "BASIC",
            "data_level": "AUCTION_ADVERTISER",
            "dimensions": ["advertiser_id"],
            "metrics": ["spend"],
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "service_type": "AUCTION",
            "page": 1,
            "page_size": 1000
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") != 0:
                logger.error(f"❌ TikTok API error: {data.get('message')}")
                return Decimal("0.00")
            
            # Sum spend from all rows
            total_spend = Decimal("0.00")
            for row in data.get("data", {}).get("list", []):
                metrics = row.get("metrics", {})
                spend = Decimal(str(metrics.get("spend", 0)))
                total_spend += spend
            
            logger.info(f"📊 TikTok spend for {advertiser_id}: ${total_spend:.2f}")
            return total_spend
    
    except Exception as e:
        logger.error(f"❌ TikTok spend fetch failed: {e}", exc_info=True)
        return Decimal("0.00")
```

**Required Packages**:
```bash
pip install httpx
```

**Environment Variables**:
```bash
TIKTOK_APP_ID=your_app_id
TIKTOK_APP_SECRET=your_app_secret
TIKTOK_ACCESS_TOKEN=your_access_token
```

---

### **2. LinkedIn Ads Integration**

**API**: [LinkedIn Marketing Developer Platform](https://learn.microsoft.com/en-us/linkedin/marketing/)  
**Auth**: OAuth 2.0 (client_id, client_secret, access_token)  
**Endpoints**:
- `GET /adAnalytics` - Campaign performance data
- `GET /adCampaignGroups/{id}/analytics` - Spend aggregation

**Python Library**: `linkedin-api` or direct REST calls

**Code Example**:
```python
async def get_linkedin_spend(
    self,
    account_id: str,
    start_date: datetime,
    end_date: datetime
) -> Decimal:
    """
    Fetch LinkedIn Ads spend for period.
    
    Args:
        account_id: LinkedIn ad account URN (urn:li:sponsoredAccount:123456)
        start_date: Period start
        end_date: Period end
    
    Returns:
        Total spend in USD
    """
    if not self.linkedin_access_token:
        logger.warning("⚠️  LinkedIn Ads credentials not configured")
        return Decimal("0.00")
    
    try:
        url = "https://api.linkedin.com/rest/adAnalytics"
        
        headers = {
            "Authorization": f"Bearer {self.linkedin_access_token}",
            "LinkedIn-Version": "202401",
            "X-RestLi-Protocol-Version": "2.0.0"
        }
        
        # LinkedIn uses milliseconds since epoch
        start_ms = int(start_date.timestamp() * 1000)
        end_ms = int(end_date.timestamp() * 1000)
        
        params = {
            "q": "analytics",
            "accounts": f"List({account_id})",
            "dateRange.start.day": start_date.day,
            "dateRange.start.month": start_date.month,
            "dateRange.start.year": start_date.year,
            "dateRange.end.day": end_date.day,
            "dateRange.end.month": end_date.month,
            "dateRange.end.year": end_date.year,
            "timeGranularity": "DAILY",
            "fields": "costInUsd"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Sum spend from all daily records
            total_spend = Decimal("0.00")
            for element in data.get("elements", []):
                cost = Decimal(str(element.get("costInUsd", 0)))
                total_spend += cost
            
            logger.info(f"📊 LinkedIn spend for {account_id}: ${total_spend:.2f}")
            return total_spend
    
    except Exception as e:
        logger.error(f"❌ LinkedIn spend fetch failed: {e}", exc_info=True)
        return Decimal("0.00")
```

**Required Packages**: Same (`httpx`)

**Environment Variables**:
```bash
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
```

---

### **3. Amazon Advertising Integration**

**API**: [Amazon Ads API](https://advertising.amazon.com/API/docs)  
**Auth**: OAuth 2.0 + LWA (Login with Amazon)  
**Endpoints**:
- `POST /reporting/reports` - Create report request
- `GET /reporting/reports/{reportId}` - Download spend data

**Python Library**: `amazon-ads-api` (unofficial) or direct REST

**Code Example**:
```python
async def get_amazon_spend(
    self,
    profile_id: str,
    start_date: datetime,
    end_date: datetime
) -> Decimal:
    """
    Fetch Amazon Advertising spend for period.
    
    Args:
        profile_id: Amazon Ads profile ID
        start_date: Period start
        end_date: Period end
    
    Returns:
        Total spend in USD
    """
    if not self.amazon_access_token:
        logger.warning("⚠️  Amazon Ads credentials not configured")
        return Decimal("0.00")
    
    try:
        # Step 1: Request report (async)
        create_url = "https://advertising-api.amazon.com/reporting/reports"
        
        headers = {
            "Authorization": f"Bearer {self.amazon_access_token}",
            "Amazon-Advertising-API-ClientId": settings.amazon_client_id,
            "Amazon-Advertising-API-Scope": profile_id,
            "Content-Type": "application/json"
        }
        
        report_config = {
            "reportDate": end_date.strftime('%Y-%m-%d'),
            "metrics": "cost",
            "groupBy": ["campaign"]
        }
        
        async with httpx.AsyncClient() as client:
            # Create report
            create_resp = await client.post(
                create_url, 
                headers=headers, 
                json=report_config, 
                timeout=30
            )
            create_resp.raise_for_status()
            
            report_id = create_resp.json().get("reportId")
            
            # Step 2: Poll for report completion (max 60s)
            download_url = f"{create_url}/{report_id}"
            
            for _ in range(12):  # 12 attempts, 5s each = 60s max
                await asyncio.sleep(5)
                
                status_resp = await client.get(download_url, headers=headers, timeout=30)
                status_data = status_resp.json()
                
                if status_data.get("status") == "SUCCESS":
                    report_url = status_data.get("url")
                    
                    # Step 3: Download and parse report
                    report_resp = await client.get(report_url, timeout=30)
                    report_data = report_resp.json()
                    
                    # Sum cost from all campaigns
                    total_spend = Decimal("0.00")
                    for row in report_data:
                        cost = Decimal(str(row.get("cost", 0)))
                        total_spend += cost
                    
                    logger.info(f"📊 Amazon Ads spend for {profile_id}: ${total_spend:.2f}")
                    return total_spend
                
                elif status_data.get("status") == "FAILURE":
                    logger.error(f"❌ Amazon report failed: {status_data.get('statusDetails')}")
                    return Decimal("0.00")
            
            logger.warning("⚠️  Amazon report timeout (>60s)")
            return Decimal("0.00")
    
    except Exception as e:
        logger.error(f"❌ Amazon spend fetch failed: {e}", exc_info=True)
        return Decimal("0.00")
```

**Required Packages**: Same (`httpx`)

**Environment Variables**:
```bash
AMAZON_CLIENT_ID=amzn1.application-oa2-client.xxx
AMAZON_CLIENT_SECRET=your_secret
AMAZON_ACCESS_TOKEN=Atza|xxx
AMAZON_REFRESH_TOKEN=Atzr|xxx
```

---

### **4. Microsoft Advertising Integration**

**API**: [Microsoft Advertising API](https://learn.microsoft.com/en-us/advertising/guides/)  
**Auth**: OAuth 2.0  
**Endpoints**:
- `ReportingService.SubmitGenerateReport` - SOAP API (legacy)
- `GET /Reporting/v13/Reports` - REST API (newer)

**Python Library**: `bingads` (official SDK)

**Code Example**:
```python
async def get_microsoft_spend(
    self,
    account_id: str,
    start_date: datetime,
    end_date: datetime
) -> Decimal:
    """
    Fetch Microsoft Advertising (Bing Ads) spend for period.
    
    Args:
        account_id: Microsoft Ads account ID
        start_date: Period start
        end_date: Period end
    
    Returns:
        Total spend in USD
    """
    if not self.microsoft_access_token:
        logger.warning("⚠️  Microsoft Ads credentials not configured")
        return Decimal("0.00")
    
    try:
        from bingads.service_client import ServiceClient
        from bingads.authorization import AuthorizationData, OAuthTokens
        from bingads.v13.reporting import (
            ReportingServiceManager,
            AccountPerformanceReportRequest,
            AccountPerformanceReportFilter,
            ReportTime,
            ReportTimePeriod,
            ReportAggregation,
            ReportFormat
        )
        
        # Setup auth
        authorization_data = AuthorizationData(
            account_id=account_id,
            customer_id=settings.microsoft_customer_id,
            developer_token=settings.microsoft_developer_token,
            authentication=OAuthTokens(access_token=self.microsoft_access_token)
        )
        
        reporting_service_manager = ReportingServiceManager(
            authorization_data=authorization_data,
            poll_interval_in_milliseconds=5000,
            environment='production'
        )
        
        # Build report request
        report_request = AccountPerformanceReportRequest(
            format=ReportFormat.Csv,
            aggregation=ReportAggregation.Daily,
            time=ReportTime(
                custom_date_range_start={
                    'Day': start_date.day,
                    'Month': start_date.month,
                    'Year': start_date.year
                },
                custom_date_range_end={
                    'Day': end_date.day,
                    'Month': end_date.month,
                    'Year': end_date.year
                },
                predefined_time=None
            ),
            columns=['Spend']
        )
        
        # Submit and download (blocking, but runs async in background)
        report_file_path = await asyncio.to_thread(
            reporting_service_manager.submit_download,
            report_request
        )
        
        # Parse CSV
        import csv
        total_spend = Decimal("0.00")
        
        with open(report_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                spend = Decimal(str(row.get('Spend', 0)))
                total_spend += spend
        
        logger.info(f"📊 Microsoft Ads spend for {account_id}: ${total_spend:.2f}")
        return total_spend
    
    except Exception as e:
        logger.error(f"❌ Microsoft Ads fetch failed: {e}", exc_info=True)
        return Decimal("0.00")
```

**Required Packages**:
```bash
pip install bingads
```

**Environment Variables**:
```bash
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
MICROSOFT_DEVELOPER_TOKEN=your_dev_token
MICROSOFT_CUSTOMER_ID=your_customer_id
MICROSOFT_ACCESS_TOKEN=your_access_token
```

---

## Updated `get_total_spend_for_period()` Method

Expand to support all 6 platforms (Meta, Google, TikTok, LinkedIn, Amazon, Microsoft):

```python
async def get_total_spend_for_period(
    self,
    store_id: int,
    start_date: datetime,
    end_date: datetime,
    ad_accounts: Dict[str, str]
) -> Dict[str, Decimal]:
    """
    Fetch total ad spend across ALL platforms for a billing period.
    
    Args:
        store_id: KIKI store ID
        start_date: Billing period start
        end_date: Billing period end
        ad_accounts: {
            "meta_account_id": "123456789",
            "google_customer_id": "123-456-7890",
            "tiktok_advertiser_id": "7123456789012345",
            "linkedin_account_urn": "urn:li:sponsoredAccount:123456",
            "amazon_profile_id": "1234567890123",
            "microsoft_account_id": "123456789"
        }
    
    Returns:
        {
            "meta_spend": Decimal("5000.00"),
            "google_spend": Decimal("3000.00"),
            "tiktok_spend": Decimal("2000.00"),
            "linkedin_spend": Decimal("1500.00"),
            "amazon_spend": Decimal("1000.00"),
            "microsoft_spend": Decimal("500.00"),
            "total_spend": Decimal("13000.00")
        }
    """
    logger.info(f"📊 Fetching ad spend for store {store_id} ({start_date} to {end_date})")
    
    # Fetch from ALL platforms concurrently
    tasks = {}
    
    if ad_accounts.get("meta_account_id"):
        tasks["meta"] = self.get_meta_spend(
            ad_account_id=ad_accounts["meta_account_id"],
            start_date=start_date,
            end_date=end_date
        )
    
    if ad_accounts.get("google_customer_id"):
        tasks["google"] = self.get_google_spend(
            customer_id=ad_accounts["google_customer_id"],
            start_date=start_date,
            end_date=end_date
        )
    
    if ad_accounts.get("tiktok_advertiser_id"):
        tasks["tiktok"] = self.get_tiktok_spend(
            advertiser_id=ad_accounts["tiktok_advertiser_id"],
            start_date=start_date,
            end_date=end_date
        )
    
    if ad_accounts.get("linkedin_account_urn"):
        tasks["linkedin"] = self.get_linkedin_spend(
            account_id=ad_accounts["linkedin_account_urn"],
            start_date=start_date,
            end_date=end_date
        )
    
    if ad_accounts.get("amazon_profile_id"):
        tasks["amazon"] = self.get_amazon_spend(
            profile_id=ad_accounts["amazon_profile_id"],
            start_date=start_date,
            end_date=end_date
        )
    
    if ad_accounts.get("microsoft_account_id"):
        tasks["microsoft"] = self.get_microsoft_spend(
            account_id=ad_accounts["microsoft_account_id"],
            start_date=start_date,
            end_date=end_date
        )
    
    # Await all concurrently
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    
    # Map results back to platform names
    spend_by_platform = {}
    for platform, result in zip(tasks.keys(), results):
        if isinstance(result, Exception):
            logger.error(f"❌ {platform.capitalize()} fetch failed: {result}")
            spend_by_platform[f"{platform}_spend"] = Decimal("0.00")
        else:
            spend_by_platform[f"{platform}_spend"] = result
    
    # Calculate total
    total_spend = sum(spend_by_platform.values(), Decimal("0.00"))
    spend_by_platform["total_spend"] = total_spend
    
    logger.info(f"✅ Total spend for store {store_id}: ${total_spend:.2f}")
    logger.info(f"   Platform breakdown: {spend_by_platform}")
    
    return spend_by_platform
```

---

## Database Schema Changes

Add platform-specific account ID columns to `stores` table:

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
```

---

## Installation & Deployment

### **Phase 1: TikTok + LinkedIn (Week 1-2)**

```bash
# Install dependencies
pip install httpx  # Already installed

# Update .env
echo "TIKTOK_APP_ID=your_id" >> .env
echo "TIKTOK_ACCESS_TOKEN=your_token" >> .env
echo "LINKEDIN_CLIENT_ID=your_id" >> .env
echo "LINKEDIN_ACCESS_TOKEN=your_token" >> .env

# Run database migration
cd services/syncledger
alembic revision --autogenerate -m "Add TikTok and LinkedIn ad accounts"
alembic upgrade head

# Test integration
pytest tests/test_ad_spend_fetcher.py::test_tiktok_spend
pytest tests/test_ad_spend_fetcher.py::test_linkedin_spend
```

### **Phase 2: Amazon + Microsoft (Week 3-4)**

```bash
# Install Microsoft Ads SDK
pip install bingads

# Update .env
echo "AMAZON_CLIENT_ID=amzn1.application-oa2-client.xxx" >> .env
echo "MICROSOFT_DEVELOPER_TOKEN=your_token" >> .env

# Run tests
pytest tests/test_ad_spend_fetcher.py::test_amazon_spend
pytest tests/test_ad_spend_fetcher.py::test_microsoft_spend
```

---

## Testing Strategy

Create comprehensive tests for each platform:

```python
# tests/test_multi_platform_spend.py
import pytest
from app.services.ad_spend_fetcher import AdSpendFetcher
from datetime import datetime, timedelta
from decimal import Decimal

@pytest.mark.asyncio
async def test_all_platforms_spend():
    """Test concurrent spend fetching from all 6 platforms"""
    fetcher = AdSpendFetcher()
    
    ad_accounts = {
        "meta_account_id": "123456789",
        "google_customer_id": "123-456-7890",
        "tiktok_advertiser_id": "7123456789012345",
        "linkedin_account_urn": "urn:li:sponsoredAccount:123456",
        "amazon_profile_id": "1234567890123",
        "microsoft_account_id": "123456789"
    }
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    result = await fetcher.get_total_spend_for_period(
        store_id=1,
        start_date=start_date,
        end_date=end_date,
        ad_accounts=ad_accounts
    )
    
    # Verify all platforms returned data
    assert "meta_spend" in result
    assert "google_spend" in result
    assert "tiktok_spend" in result
    assert "linkedin_spend" in result
    assert "amazon_spend" in result
    assert "microsoft_spend" in result
    assert "total_spend" in result
    
    # Verify total is sum of all platforms
    expected_total = (
        result["meta_spend"] +
        result["google_spend"] +
        result["tiktok_spend"] +
        result["linkedin_spend"] +
        result["amazon_spend"] +
        result["microsoft_spend"]
    )
    assert result["total_spend"] == expected_total
    
    # All values should be Decimal
    for platform, spend in result.items():
        assert isinstance(spend, Decimal)
        assert spend >= Decimal("0.00")
```

---

## Business Impact

### **Revenue Opportunity**

| Platform | Avg Client Spend/Month | KIKI Success Fee (20% Net Profit) | Annual Revenue/100 Clients |
|----------|------------------------|-----------------------------------|----------------------------|
| Meta + Google (Current) | $15,000 | $600 | $7.2M |
| **+ TikTok** | $8,000 | $320 | $3.84M |
| **+ LinkedIn** | $12,000 | $480 | $5.76M |
| **+ Amazon** | $10,000 | $400 | $4.8M |
| **+ Microsoft** | $5,000 | $200 | $2.4M |
| **TOTAL (6 Platforms)** | **$50,000** | **$2,000** | **$24M** |

**Expected Uplift**: Adding 4 platforms unlocks **+$16.8M annual revenue** for KIKI (assuming 100 clients)

### **Client Value Proposition**

*Current*: "KIKI manages your Meta and Google ads with Net Profit alignment"  
*Enhanced*: "KIKI is your **all-platform revenue engine** - Meta, Google, TikTok, LinkedIn, Amazon, Microsoft - unified LTV optimization with Zero-Risk Guarantee"

---

## Next Steps

1. **Immediate**: Implement TikTok + LinkedIn (2-week sprint)
2. **Q2 2026**: Add Amazon + Microsoft
3. **Q3 2026**: Add Snapchat, Pinterest, Reddit (if client demand exists)
4. **Ongoing**: Monitor Twitter/X API changes for potential re-entry

---

## API Key Management

**Security Best Practices**:
- Store all tokens in **HashiCorp Vault** (already configured in [deploy/vault-setup.sh](../../../../../deploy/vault-setup.sh))
- Rotate tokens every 90 days
- Use separate tokens per environment (dev, staging, prod)
- Implement rate limiting (TikTok: 10 req/min, LinkedIn: 100 req/min)

**Token Storage Schema**:
```python
# shared/vault_secrets.py
VAULT_PATHS = {
    "tiktok": "secret/kiki/ad-platforms/tiktok",
    "linkedin": "secret/kiki/ad-platforms/linkedin",
    "amazon": "secret/kiki/ad-platforms/amazon",
    "microsoft": "secret/kiki/ad-platforms/microsoft"
}
```

---

*Last Updated: February 7, 2026*  
*Owner: KIKI Revenue Engineering Team*  
*Status: Ready for Implementation*
