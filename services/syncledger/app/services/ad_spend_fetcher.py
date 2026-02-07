"""
Ad Platform Spend Fetcher Service

Fetches daily ad spend from Meta Ads and Google Ads APIs.
Used by SyncLedger to calculate Net Profit Uplift.

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

import httpx
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from app.config import settings

logger = logging.getLogger(__name__)


class AdSpendFetcher:
    """
    Fetches ad spend data from Meta and Google Ads.
    
    Integration:
    - Meta Ads: Uses facebook-business library
    - Google Ads: Uses google-ads-python library
    
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
            self.google_ads_client = GoogleAdsClient.load_from_storage(
                settings.google_ads_credentials_path
            )
            logger.info("✅ Google Ads API initialized")
        else:
            self.google_ads_client = None
            logger.warning("⚠️  Google Ads credentials not configured")
    
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
    
    async def get_total_spend_for_period(
        self,
        store_id: int,
        start_date: datetime,
        end_date: datetime,
        ad_accounts: Dict[str, str]
    ) -> Dict[str, Decimal]:
        """
        Fetch total ad spend across all platforms for a billing period.
        
        Args:
            store_id: KIKI store ID
            start_date: Billing period start
            end_date: Billing period end
            ad_accounts: {
                "meta_account_id": "123456789",
                "google_customer_id": "123-456-7890"
            }
        
        Returns:
            {
                "meta_spend": Decimal("5000.00"),
                "google_spend": Decimal("3000.00"),
                "total_spend": Decimal("8000.00")
            }
        """
        logger.info(f"📊 Fetching ad spend for store {store_id} ({start_date} to {end_date})")
        
        # Fetch from both platforms concurrently
        meta_task = None
        google_task = None
        
        if ad_accounts.get("meta_account_id"):
            meta_task = self.get_meta_spend(
                ad_account_id=ad_accounts["meta_account_id"],
                start_date=start_date,
                end_date=end_date
            )
        
        if ad_accounts.get("google_customer_id"):
            google_task = self.get_google_spend(
                customer_id=ad_accounts["google_customer_id"],
                start_date=start_date,
                end_date=end_date
            )
        
        # Await both
        meta_spend = await meta_task if meta_task else Decimal("0.00")
        google_spend = await google_task if google_task else Decimal("0.00")
        
        total_spend = meta_spend + google_spend
        
        result = {
            "meta_spend": meta_spend,
            "google_spend": google_spend,
            "total_spend": total_spend
        }
        
        logger.info(f"✅ Total spend for store {store_id}: ${total_spend:.2f}")
        return result
    
    async def get_baseline_spend(
        self,
        store_id: int,
        baseline_start: datetime,
        baseline_end: datetime,
        ad_accounts: Dict[str, str]
    ) -> Decimal:
        """
        Calculate baseline ad spend (12-month historical average).
        
        Used for Net Uplift calculation:
        Net = (New Revenue - Baseline Revenue) - (New Spend - Baseline Spend)
        
        Args:
            store_id: KIKI store ID
            baseline_start: 12 months before KIKI installation
            baseline_end: KIKI installation date
            ad_accounts: Platform account IDs
        
        Returns:
            Monthly average baseline spend
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


class MarginGuardian:
    """
    Safety Governor for SyncFlow bidding.
    
    Purpose: Prevent KIKI from spending more on ads than the projected uplift.
    
    Rule: If CPA (Cost Per Acquisition) exceeds LTV (Lifetime Value from SyncValue),
          automatically kill the bid to protect client's Net Profit.
    
    Example:
    - SyncValue predicts LTV = $50 for new customer
    - SyncFlow's current CPA = $45 → ✅ Continue bidding
    - CPA increases to $55 → 🛑 Kill bid (unprofitable)
    """
    
    def __init__(self, safety_margin: float = 0.10):
        """
        Initialize with safety margin.
        
        Args:
            safety_margin: Buffer below LTV (default 10%)
                          Example: LTV $100, margin 10% → Max CPA = $90
        """
        self.safety_margin = safety_margin
        logger.info(f"🛡️  MarginGuardian initialized with {safety_margin * 100}% safety buffer")
    
    def should_kill_bid(
        self,
        current_cpa: Decimal,
        predicted_ltv: Decimal,
        campaign_id: str
    ) -> tuple[bool, str]:
        """
        Determine if bid should be killed to protect margin.
        
        Args:
            current_cpa: Current Cost Per Acquisition
            predicted_ltv: Lifetime Value from SyncValue
            campaign_id: Campaign being evaluated
        
        Returns:
            (should_kill: bool, reason: str)
        """
        # Calculate max acceptable CPA (LTV - safety buffer)
        max_cpa = predicted_ltv * (Decimal("1.0") - Decimal(str(self.safety_margin)))
        
        if current_cpa > max_cpa:
            reason = (
                f"🛑 MARGIN GUARDIAN TRIGGERED: Campaign {campaign_id} "
                f"CPA ${current_cpa:.2f} exceeds max ${max_cpa:.2f} "
                f"(LTV ${predicted_ltv:.2f} - {self.safety_margin * 100}% buffer). "
                f"Killing bid to protect client Net Profit."
            )
            logger.warning(reason)
            return True, reason
        
        # Safe to continue
        margin_remaining = max_cpa - current_cpa
        reason = (
            f"✅ Campaign {campaign_id} safe: "
            f"CPA ${current_cpa:.2f} < Max ${max_cpa:.2f}. "
            f"Margin remaining: ${margin_remaining:.2f}"
        )
        logger.info(reason)
        return False, reason
    
    def calculate_safe_bid_ceiling(
        self,
        predicted_ltv: Decimal,
        conversion_rate: float
    ) -> Decimal:
        """
        Calculate maximum safe bid amount.
        
        Formula:
        Max Bid = (LTV × (1 - SafetyMargin)) × ConversionRate
        
        Example:
        - LTV = $100
        - Safety Margin = 10%
        - Conversion Rate = 2%
        - Max Bid = ($100 × 0.90) × 0.02 = $1.80
        
        Args:
            predicted_ltv: Customer lifetime value
            conversion_rate: Expected click→sale rate
        
        Returns:
            Maximum bid amount in USD
        """
        max_cpa = predicted_ltv * (Decimal("1.0") - Decimal(str(self.safety_margin)))
        max_bid = max_cpa * Decimal(str(conversion_rate))
        
        logger.info(f"💰 Safe bid ceiling: ${max_bid:.2f} (LTV ${predicted_ltv}, CVR {conversion_rate * 100}%)")
        return max_bid
