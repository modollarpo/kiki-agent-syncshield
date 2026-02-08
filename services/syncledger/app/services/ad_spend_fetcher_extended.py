"""
Multi-Platform Ad Spend Fetcher Service (Extended)

Fetches daily ad spend from 6 major ad platforms:
- Meta Ads (Facebook/Instagram) ✅
- Google Ads ✅
- TikTok Ads 🆕
- LinkedIn Ads 🆕
- Amazon Advertising 🆕
- Microsoft Advertising (Bing) 🆕

Used by SyncLedger to calculate Net Profit Uplift across all platforms.

Formula:
Net Uplift = (New Revenue - Baseline Revenue) - (New Ad Spend - Baseline Ad Spend)
Success Fee = Net Uplift × 20%

Client maintains their own ad accounts (security + data ownership).
KIKI has API-only access for budget management and optimization.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
import asyncio
import csv
import tempfile

import httpx
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Import settings from local config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from config import settings

logger = logging.getLogger(__name__)


class AdSpendFetcherExtended:
    """
    Fetches ad spend data from 6 major platforms.
    
    Integration:
    - Meta Ads: facebook-business library
    - Google Ads: google-ads-python library
    - TikTok Ads: Direct REST API calls
    - LinkedIn Ads: Direct REST API calls
    - Amazon Ads: Direct REST API calls
    - Microsoft Ads: bingads library
    
    Returns:
    - Daily spend totals by platform
    - Monthly aggregated spend
    - Baseline spend (12-month historical average)
    """
    
    def __init__(self):
        # Meta Ads API initialization
        if settings.meta_access_token:
            FacebookAdsApi.init(
                app_id=settings.meta_app_id,
                app_secret=settings.meta_app_secret,
                access_token=settings.meta_access_token
            )
            logger.info("✅ Meta Ads API initialized")
        else:
            logger.warning("⚠️  Meta Ads credentials not configured")
        
        # Google Ads API initialization
        if settings.google_ads_credentials_path:
            try:
                self.google_ads_client = GoogleAdsClient.load_from_storage(
                    settings.google_ads_credentials_path
                )
                logger.info("✅ Google Ads API initialized")
            except FileNotFoundError:
                self.google_ads_client = None
                logger.warning(f"⚠️  Google Ads credentials file not found: {settings.google_ads_credentials_path}")
            except Exception as e:
                self.google_ads_client = None
                logger.warning(f"⚠️  Google Ads initialization failed: {e}")
        else:
            self.google_ads_client = None
            logger.warning("⚠️  Google Ads credentials not configured")
        
        # TikTok Ads - REST API (no official Python SDK)
        self.tiktok_access_token = getattr(settings, 'tiktok_access_token', None)
        if self.tiktok_access_token:
            logger.info("✅ TikTok Ads API initialized")
        else:
            logger.warning("⚠️  TikTok Ads credentials not configured")
        
        # LinkedIn Ads - REST API
        self.linkedin_access_token = getattr(settings, 'linkedin_access_token', None)
        if self.linkedin_access_token:
            logger.info("✅ LinkedIn Ads API initialized")
        else:
            logger.warning("⚠️  LinkedIn Ads credentials not configured")
        
        # Amazon Advertising - REST API
        self.amazon_access_token = getattr(settings, 'amazon_access_token', None)
        self.amazon_client_id = getattr(settings, 'amazon_client_id', None)
        if self.amazon_access_token:
            logger.info("✅ Amazon Ads API initialized")
        else:
            logger.warning("⚠️  Amazon Ads credentials not configured")
        
        # Microsoft Advertising - Official SDK
        self.microsoft_access_token = getattr(settings, 'microsoft_access_token', None)
        if self.microsoft_access_token:
            logger.info("✅ Microsoft Ads API initialized")
        else:
            logger.warning("⚠️  Microsoft Ads credentials not configured")
    
    # ============================================================================
    # META ADS (Facebook/Instagram)
    # ============================================================================
    
    async def get_meta_spend(
        self,
        ad_account_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Decimal:
        """
        Fetch total Meta Ads spend for period.
        
        Args:
            ad_account_id: Meta ad account ID (act_xxxxx)
            start_date: Start of period
            end_date: End of period
        
        Returns:
            Total spend in USD
        """
        try:
            account = AdAccount(f"act_{ad_account_id}")
            
            params = {
                'time_range': {
                    'since': start_date.strftime('%Y-%m-%d'),
                    'until': end_date.strftime('%Y-%m-%d')
                },
                'level': 'account',
                'fields': [AdsInsights.Field.spend]
            }
            
            insights = account.get_insights(params=params)
            
            total_spend = Decimal("0.00")
            for insight in insights:
                spend = Decimal(str(insight.get('spend', 0)))
                total_spend += spend
            
            logger.info(f"📊 Meta spend for {ad_account_id}: ${total_spend:.2f}")
            return total_spend
            
        except Exception as e:
            logger.error(f"❌ Meta spend fetch failed for {ad_account_id}: {e}", exc_info=True)
            return Decimal("0.00")
    
    # ============================================================================
    # GOOGLE ADS
    # ============================================================================
    
    async def get_google_spend(
        self,
        customer_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Decimal:
        """
        Fetch total Google Ads spend for period.
        
        Args:
            customer_id: Google Ads customer ID (xxx-xxx-xxxx)
            start_date: Start of period
            end_date: End of period
        
        Returns:
            Total spend in USD (converted from micros)
        """
        if not self.google_ads_client:
            logger.warning("⚠️  Google Ads client not initialized")
            return Decimal("0.00")
        
        try:
            ga_service = self.google_ads_client.get_service("GoogleAdsService")
            
            query = f"""
                SELECT
                    metrics.cost_micros,
                    segments.date
                FROM customer
                WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}' 
                    AND '{end_date.strftime('%Y-%m-%d')}'
            """
            
            response = ga_service.search_stream(
                customer_id=customer_id.replace('-', ''),
                query=query
            )
            
            total_micros = 0
            for batch in response:
                for row in batch.results:
                    total_micros += row.metrics.cost_micros
            
            # Convert micros to dollars (1 micro = $0.000001)
            total_spend = Decimal(total_micros) / Decimal(1_000_000)
            
            logger.info(f"📊 Google Ads spend for {customer_id}: ${total_spend:.2f}")
            return total_spend
            
        except GoogleAdsException as e:
            logger.error(f"❌ Google Ads fetch failed for {customer_id}: {e}", exc_info=True)
            return Decimal("0.00")
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching Google spend: {e}", exc_info=True)
            return Decimal("0.00")
    
    # ============================================================================
    # TIKTOK ADS 🆕
    # ============================================================================
    
    async def get_tiktok_spend(
        self,
        advertiser_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Decimal:
        """
        Fetch TikTok Ads spend for period.
        
        API: https://ads.tiktok.com/marketing_api/docs
        
        Args:
            advertiser_id: TikTok advertiser ID (numeric string)
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
                response = await client.get(
                    url, 
                    headers=headers, 
                    json=payload, 
                    timeout=30
                )
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
    
    # ============================================================================
    # LINKEDIN ADS 🆕
    # ============================================================================
    
    async def get_linkedin_spend(
        self,
        account_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Decimal:
        """
        Fetch LinkedIn Ads spend for period.
        
        API: https://learn.microsoft.com/en-us/linkedin/marketing/
        
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
                response = await client.get(
                    url, 
                    headers=headers, 
                    params=params, 
                    timeout=30
                )
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
    
    # ============================================================================
    # AMAZON ADVERTISING 🆕
    # ============================================================================
    
    async def get_amazon_spend(
        self,
        profile_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Decimal:
        """
        Fetch Amazon Advertising spend for period.
        
        API: https://advertising.amazon.com/API/docs
        
        Note: Amazon Ads API is asynchronous - must request report, poll for completion,
        then download CSV. This can take 30-60 seconds.
        
        Args:
            profile_id: Amazon Ads profile ID
            start_date: Period start
            end_date: Period end
        
        Returns:
            Total spend in USD
        """
        if not self.amazon_access_token or not self.amazon_client_id:
            logger.warning("⚠️  Amazon Ads credentials not configured")
            return Decimal("0.00")
        
        try:
            # Step 1: Request report (async)
            create_url = "https://advertising-api.amazon.com/reporting/reports"
            
            headers = {
                "Authorization": f"Bearer {self.amazon_access_token}",
                "Amazon-Advertising-API-ClientId": self.amazon_client_id,
                "Amazon-Advertising-API-Scope": profile_id,
                "Content-Type": "application/json"
            }
            
            # Request cost report for date range
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
                logger.info(f"📊 Amazon report requested: {report_id}")
                
                # Step 2: Poll for report completion (max 60s)
                download_url = f"{create_url}/{report_id}"
                
                for attempt in range(12):  # 12 attempts, 5s each = 60s max
                    await asyncio.sleep(5)
                    
                    status_resp = await client.get(download_url, headers=headers, timeout=30)
                    status_data = status_resp.json()
                    
                    status = status_data.get("status")
                    logger.debug(f"Amazon report status (attempt {attempt+1}): {status}")
                    
                    if status == "SUCCESS":
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
                    
                    elif status == "FAILURE":
                        logger.error(f"❌ Amazon report failed: {status_data.get('statusDetails')}")
                        return Decimal("0.00")
                
                logger.warning("⚠️  Amazon report timeout (>60s)")
                return Decimal("0.00")
        
        except Exception as e:
            logger.error(f"❌ Amazon spend fetch failed: {e}", exc_info=True)
            return Decimal("0.00")
    
    # ============================================================================
    # MICROSOFT ADVERTISING (Bing Ads) 🆕
    # ============================================================================
    
    async def get_microsoft_spend(
        self,
        account_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Decimal:
        """
        Fetch Microsoft Advertising (Bing Ads) spend for period.
        
        API: https://learn.microsoft.com/en-us/advertising/guides/
        
        Note: Uses official bingads SDK. Report generation is synchronous
        and blocks until CSV is ready.
        
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
                ReportTime,
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
            logger.info(f"📊 Requesting Microsoft Ads report for {account_id}...")
            report_file_path = await asyncio.to_thread(
                reporting_service_manager.submit_download,
                report_request
            )
            
            # Parse CSV
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
    
    # ============================================================================
    # MULTI-PLATFORM AGGREGATION
    # ============================================================================
    
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
        
        # Fill in zeros for platforms not configured
        for platform in ["meta", "google", "tiktok", "linkedin", "amazon", "microsoft"]:
            key = f"{platform}_spend"
            if key not in spend_by_platform:
                spend_by_platform[key] = Decimal("0.00")
        
        # Calculate total
        total_spend = sum(spend_by_platform.values(), Decimal("0.00"))
        spend_by_platform["total_spend"] = total_spend
        
        logger.info(f"✅ Total spend for store {store_id}: ${total_spend:.2f}")
        logger.info(f"   Platform breakdown: {spend_by_platform}")
        
        return spend_by_platform
    
    async def get_baseline_spend(
        self,
        store_id: int,
        baseline_start: datetime,
        baseline_end: datetime,
        ad_accounts: Dict[str, str]
    ) -> Decimal:
        """
        Calculate baseline ad spend across all platforms (12-month historical average).
        
        Used for Net Uplift calculation:
        Net = (New Revenue - Baseline Revenue) - (New Spend - Baseline Spend)
        
        Args:
            store_id: KIKI store ID
            baseline_start: 12 months before KIKI installation
            baseline_end: KIKI installation date
            ad_accounts: Platform account IDs
        
        Returns:
            Monthly average baseline spend (all platforms combined)
        """
        logger.info(f"📊 Calculating baseline spend for store {store_id}")
        
        spend_data = await self.get_total_spend_for_period(
            store_id=store_id,
            start_date=baseline_start,
            end_date=baseline_end,
            ad_accounts=ad_accounts
        )
        
        total_baseline_spend = spend_data["total_spend"]
        
        # Calculate months in baseline period
        months = (baseline_end.year - baseline_start.year) * 12 + \
                 (baseline_end.month - baseline_start.month)
        
        if months == 0:
            months = 1
        
        baseline_monthly_avg = total_baseline_spend / Decimal(months)
        
        logger.info(f"✅ Baseline monthly spend for store {store_id}: ${baseline_monthly_avg:.2f}")
        return baseline_monthly_avg
