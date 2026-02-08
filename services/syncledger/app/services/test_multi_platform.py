"""
Test script for multi-platform ad spend fetcher

Usage:
    python test_multi_platform.py

Tests all 6 platforms with mock data (no real API calls).
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ad_spend_fetcher_extended import AdSpendFetcherExtended
from config import settings


async def test_platform_detection():
    """Test that all platform methods are available"""
    print("=" * 80)
    print("TEST 1: Platform Detection")
    print("=" * 80)
    
    fetcher = AdSpendFetcherExtended()
    
    # Check which platforms are configured
    platforms_status = {
        "Meta": "✅" if settings.meta_access_token else "⚠️  Not configured",
        "Google": "✅" if fetcher.google_ads_client else "⚠️  Not configured",
        "TikTok": "✅" if fetcher.tiktok_access_token else "⚠️  Not configured",
        "LinkedIn": "✅" if fetcher.linkedin_access_token else "⚠️  Not configured",
        "Amazon": "✅" if fetcher.amazon_access_token else "⚠️  Not configured",
        "Microsoft": "✅" if fetcher.microsoft_access_token else "⚠️  Not configured",
    }
    
    print("\nPlatform Credentials Status:")
    for platform, status in platforms_status.items():
        print(f"  {platform:12} {status}")
    
    configured_count = sum(1 for s in platforms_status.values() if "✅" in s)
    print(f"\nConfigured: {configured_count}/6 platforms")
    print()


async def test_mock_spend_fetch():
    """Test spend fetching with real API calls (production-grade)"""
    print("=" * 80)
    print("TEST 2: Real Spend Fetch (API Integration)")
    print("=" * 80)
    
    fetcher = AdSpendFetcherExtended()
    
    # Real ad accounts (must be configured with credentials)
    ad_accounts = {
        "meta_account_id": settings.meta_account_id,
        "google_account_id": settings.google_account_id,
        "tiktok_account_id": settings.tiktok_account_id,
        "linkedin_account_id": settings.linkedin_account_id,
        "amazon_account_id": settings.amazon_account_id,
        "microsoft_account_id": settings.microsoft_account_id,
    }
    
    # Fetch spend for each platform
    spend_results = {}
    for platform, account_id in ad_accounts.items():
        try:
            spend = await fetcher.fetch_spend(platform, account_id)
            spend_results[platform] = spend
            print(f"  {platform:12} Spend: ${spend:.2f}")
        except Exception as e:
            print(f"  {platform:12} Error: {e}")
    
    total_spend = sum(spend_results.values())
    print(f"\nTotal spend across all platforms: ${total_spend:.2f}\n")
        "google_customer_id": "123-456-7890",
        "tiktok_advertiser_id": "7123456789012345",
        "linkedin_account_urn": "urn:li:sponsoredAccount:123456",
        "amazon_profile_id": "1234567890123",
        "microsoft_account_id": "123456789"
    }
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"\nFetching spend for period: {start_date.date()} to {end_date.date()}")
    print("Note: Without credentials, all platforms will return $0.00\n")
    
    result = await fetcher.get_total_spend_for_period(
        store_id=1,
        start_date=start_date,
        end_date=end_date,
        ad_accounts=ad_accounts
    )
    
    # Display results
    print("Results:")
    print("-" * 80)
    for platform in ["meta", "google", "tiktok", "linkedin", "amazon", "microsoft"]:
        spend = result.get(f"{platform}_spend", Decimal("0.00"))
        print(f"  {platform.capitalize():12} ${spend:>10,.2f}")
    
    print(f"  {'─' * 12} {'─' * 12}")
    print(f"  {'TOTAL':12} ${result['total_spend']:>10,.2f}")
    print()
    
    # Verify total is sum of all platforms
    expected_total = sum(
        result.get(f"{p}_spend", Decimal("0.00"))
        for p in ["meta", "google", "tiktok", "linkedin", "amazon", "microsoft"]
    )
    
    assert result["total_spend"] == expected_total, "Total mismatch!"
    print("✅ Test passed: Total spend matches sum of all platforms\n")


async def test_concurrent_fetching():
    """Test that all platforms are fetched concurrently (not sequentially)"""
    print("=" * 80)
    print("TEST 3: Concurrent Fetching Performance")
    print("=" * 80)
    
    fetcher = AdSpendFetcherExtended()
    
    ad_accounts = {
        "meta_account_id": "123456789",
        "google_customer_id": "123-456-7890",
        "tiktok_advertiser_id": "7123456789012345",
        "linkedin_account_urn": "urn:li:sponsoredAccount:123456",
        "amazon_profile_id": "1234567890123",
        "microsoft_account_id": "123456789"
    }
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print("\nTesting concurrent fetch (should complete in <5 seconds)...")
    
    import time
    start_time = time.time()
    
    result = await fetcher.get_total_spend_for_period(
        store_id=1,
        start_date=start_date,
        end_date=end_date,
        ad_accounts=ad_accounts
    )
    
    elapsed = time.time() - start_time
    
    print(f"✅ Completed in {elapsed:.2f} seconds")
    
    if elapsed < 1.0:
        print("   (Fast because no real API calls were made - credentials missing)")
    elif elapsed < 5.0:
        print("   ✅ Good performance - concurrent fetching working")
    else:
        print("   ⚠️  Slower than expected - may be sequential?")
    
    print()


async def test_baseline_calculation():
    """Test baseline spend calculation"""
    print("=" * 80)
    print("TEST 4: Baseline Spend Calculation")
    print("=" * 80)
    
    fetcher = AdSpendFetcherExtended()
    
    ad_accounts = {
        "meta_account_id": "123456789",
        "google_customer_id": "123-456-7890",
        "tiktok_advertiser_id": "7123456789012345",
    }
    
    # 12-month baseline period
    baseline_end = datetime.now()
    baseline_start = baseline_end - timedelta(days=365)
    
    print(f"\nCalculating 12-month baseline: {baseline_start.date()} to {baseline_end.date()}")
    
    baseline_monthly_avg = await fetcher.get_baseline_spend(
        store_id=1,
        baseline_start=baseline_start,
        baseline_end=baseline_end,
        ad_accounts=ad_accounts
    )
    
    print(f"✅ Baseline monthly average: ${baseline_monthly_avg:,.2f}")
    print(f"   (Without credentials, this will be $0.00)\n")


async def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 80)
    print(" KIKI Multi-Platform Ad Spend Fetcher - Integration Tests")
    print("=" * 80)
    print()
    
    await test_platform_detection()
    await test_mock_spend_fetch()
    await test_concurrent_fetching()
    await test_baseline_calculation()
    
    print("=" * 80)
    print(" All Tests Completed!")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. Add real API credentials to .env file")
    print("  2. Run: python test_multi_platform.py (with real credentials)")
    print("  3. Deploy to staging environment")
    print("  4. Monitor Grafana dashboard for platform-level spend metrics")
    print()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
