"""
SyncScrape Example - End-to-End Demonstration

This script demonstrates the complete SyncScrape workflow:
1. Extract brand identity from a real website
2. Generate campaign brief via SyncBrain
3. Create ad variations via SyncCreate
4. Validate assets via SyncShield

Run: python example_scrape.py
"""

import asyncio
import json
import logging
from scraper import SyncScrapeOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_scrape(url: str):
    """
    Demonstrate the SyncScrape workflow with a real URL.
    
    Args:
        url: Target website to scrape
    """
    print(f"\n{'='*80}")
    print(f"SyncScrape Demo - Brand Intelligence & Campaign Generation")
    print(f"{'='*80}\n")
    
    print(f"📍 Target URL: {url}\n")
    
    # Initialize orchestrator
    orchestrator = SyncScrapeOrchestrator(
        syncbrain_url="http://syncbrain:8001",
        synccreate_url="http://synccreate:8004",
        syncshield_url="http://syncshield:8006"
    )
    
    try:
        # Execute workflow
        print("🚀 Starting SyncScrape workflow...\n")
        
        result = await orchestrator.execute(
            url=url,
            campaign_goal="brand awareness and customer acquisition",
            num_ad_copies=5,
            num_image_prompts=3
        )
        
        # Display results
        print(f"\n{'='*80}")
        print(f"✅ WORKFLOW COMPLETED SUCCESSFULLY")
        print(f"{'='*80}\n")
        
        # Brand Identity Summary
        brand = result['brand_identity']
        print("🏢 BRAND IDENTITY")
        print(f"   Name: {brand.get('brand_name', 'N/A')}")
        print(f"   Tone: {brand.get('tone', 'N/A')}")
        print(f"   Colors: {', '.join(brand.get('primary_colors', []))}")
        print(f"   Products: {len(brand.get('product_catalog', []))}")
        print(f"   Keywords: {', '.join(brand.get('keywords', [])[:5])}")
        
        # Campaign Brief Summary
        brief = result['campaign_brief']
        print(f"\n📋 CAMPAIGN BRIEF")
        print(f"   ID: {brief.get('campaign_id')}")
        print(f"   Target: {brief.get('target_audience')}")
        print(f"   Message: {brief.get('key_message')[:80]}...")
        
        # Generated Assets
        assets = result['generated_assets']
        print(f"\n📝 AD COPY VARIATIONS ({len(assets['copies'])})")
        for i, copy in enumerate(assets['copies'], 1):
            status_icon = "✅" if copy['brand_safe'] else "❌"
            print(f"\n   {i}. {status_icon} {copy['asset_id']}")
            print(f"      Content: {copy['content'][:100]}...")
            print(f"      Sentiment: {copy.get('sentiment_score', 0):.2f}")
            print(f"      Status: {copy.get('compliance_status', 'unknown')}")
        
        print(f"\n🖼️  IMAGE PROMPTS ({len(assets['image_prompts'])})")
        for i, prompt in enumerate(assets['image_prompts'], 1):
            status_icon = "✅" if prompt['brand_safe'] else "❌"
            print(f"\n   {i}. {status_icon} {prompt['asset_id']}")
            print(f"      Prompt: {prompt['content'][:100]}...")
            print(f"      Sentiment: {prompt.get('sentiment_score', 0):.2f}")
        
        # Metrics
        metrics = result['metrics']
        print(f"\n📊 METRICS")
        print(f"   Total Assets: {metrics['total_assets']}")
        print(f"   Approved: {metrics['approved_assets']}")
        print(f"   Approval Rate: {metrics['approval_rate']:.1f}%")
        print(f"   Products Extracted: {metrics['extracted_products']}")
        print(f"   Colors Extracted: {metrics['extracted_colors']}")
        
        # Save to file
        output_file = f"scrape_result_{brand.get('brand_name', 'unknown').replace(' ', '_')}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n💾 Full results saved to: {output_file}")
        
        print(f"\n{'='*80}\n")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error during scrape: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")
        raise


async def run_examples():
    """Run multiple example scrapes"""
    
    # Example 1: E-commerce site (if accessible)
    print("\n" + "="*80)
    print("EXAMPLE 1: E-commerce Site")
    print("="*80)
    
    try:
        await demo_scrape("https://www.shopify.com")
    except Exception as e:
        logger.warning(f"Example 1 failed: {e}")
    
    # Example 2: SaaS company (if accessible)
    print("\n" + "="*80)
    print("EXAMPLE 2: SaaS Platform")
    print("="*80)
    
    try:
        await demo_scrape("https://www.stripe.com")
    except Exception as e:
        logger.warning(f"Example 2 failed: {e}")
    
    # Example 3: Simple site
    print("\n" + "="*80)
    print("EXAMPLE 3: Simple Website")
    print("="*80)
    
    try:
        await demo_scrape("https://example.com")
    except Exception as e:
        logger.warning(f"Example 3 failed: {e}")


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        # User provided a URL
        url = sys.argv[1]
        asyncio.run(demo_scrape(url))
    else:
        # Run examples
        print("\n💡 Usage: python example_scrape.py <url>")
        print("   Or run without arguments to see examples\n")
        
        # Ask user
        choice = input("Run example scrapes? (y/n): ").lower()
        if choice == 'y':
            asyncio.run(run_examples())
        else:
            print("\nProvide a URL to scrape:")
            url = input("URL: ").strip()
            if url:
                asyncio.run(demo_scrape(url))
            else:
                print("No URL provided. Exiting.")


if __name__ == "__main__":
    main()
