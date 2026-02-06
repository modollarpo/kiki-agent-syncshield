"""
Example: URL-to-Campaign Automation with Council of Nine

Demonstrates KIKI Agent's "Advantage+ Suite" - transforming a URL
into a complete, deployed advertising campaign.

This example shows:
1. Industry classification from URL
2. LTV baseline prediction
3. Autonomous creative generation (5 ad copies + 3 image prompts)
4. Brand safety validation
5. Optional deployment to SyncFlow with LTV constraints
"""

import asyncio
import httpx
from datetime import datetime


SYNCVALUE_URL = "http://localhost:8002"


async def example_url_to_campaign_basic():
    """
    Example 1: Basic URL-to-Campaign (Draft Mode)
    
    Generates campaign assets without deploying to SyncFlow.
    Perfect for review before deployment.
    """
    print("=" * 80)
    print("Example 1: URL-to-Campaign (Draft Mode)")
    print("=" * 80)
    print()
    
    url = "https://www.shopify.com"  # Example e-commerce platform
    
    print(f"🚀 Starting URL-to-Campaign for: {url}")
    print(f"Mode: Draft (auto_deploy=false)")
    print()
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f" {SYNCVALUE_URL}/api/v1/url-to-campaign",
                json={
                    "url": url,
                    "auto_deploy": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                deployment = result["deployment"]
                
                print("✅ Campaign Created Successfully!")
                print()
                print(f"{'Summary':-^80}")
                print(f"Deployment ID:      {deployment['deployment_id']}")
                print(f"Brand Name:         {deployment['brand_name']}")
                print(f"Industry:           {deployment['industry_category']}")
                print(f"Campaign Type:      {deployment['campaign_type']}")
                print(f"LTV Baseline:       ${deployment['ltv_baseline']:.2f}")
                print(f"Deployment Status:  {deployment['deployment_status']}")
                print()
                
                print(f"{'Brand Safety':-^80}")
                print(f"Brand Safe:         {'✅ PASS' if deployment['brand_safe'] else '⚠️ REVIEW REQUIRED'}")
                print(f"Compliance Status:  {deployment['compliance_status']}")
                print()
                
                ad_copies_count = len(deployment['ad_copies'])
                print(f"{f'Generated Ad Copies ({ad_copies_count})':-^80}")
                for i, copy in enumerate(deployment['ad_copies'], 1):
                    print(f"{i}. {copy}")
                print()
                
                image_prompts_count = len(deployment['image_prompts'])
                print(f"{f'Generated Image Prompts ({image_prompts_count})':-^80}")
                for i, prompt in enumerate(deployment['image_prompts'], 1):
                    print(f"{i}. {prompt}")
                print()
                
                print(f"{'Next Steps':-^80}")
                for step in result.get('next_steps', []):
                    print(f"• {step}")
                print()
                
                return deployment
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
        except httpx.ConnectError:
            print("❌ Error: Could not connect to SyncValue service")
            print(f"Ensure SyncValue is running on {SYNCVALUE_URL}")
        except Exception as e:
            print(f"❌ Error: {e}")


async def example_url_to_campaign_auto_deploy():
    """
    Example 2: URL-to-Campaign with Auto-Deployment
    
    Generates campaign and automatically deploys to SyncFlow
    with LTV-based bidding constraints.
    """
    print("\n" + "=" * 80)
    print("Example 2: URL-to-Campaign (Auto-Deploy Mode)")
    print("=" * 80)
    print()
    
    url = "https://www.netflix.com"  # Example subscription service
    
    print(f"🚀 Starting URL-to-Campaign for: {url}")
    print(f"Mode: Auto-Deploy (auto_deploy=true)")
    print("⚠️  Campaign will be deployed to SyncFlow if brand safety passes")
    print()
    
    async with httpx.AsyncClient(timeout=150.0) as client:
        try:
            response = await client.post(
                f"{SYNCVALUE_URL}/api/v1/url-to-campaign",
                json={
                    "url": url,
                    "auto_deploy": True
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                deployment = result["deployment"]
                
                print("✅ Campaign Processing Complete!")
                print()
                print(f"{'Deployment Summary':-^80}")
                print(f"Brand Name:         {deployment['brand_name']}")
                print(f"Industry:           {deployment['industry_category']}")
                print(f"Campaign Type:      {deployment['campaign_type']}")
                print(f"LTV Baseline:       ${deployment['ltv_baseline']:.2f}")
                print()
                
                print(f"{'Deployment Status':-^80}")
                print(f"Status:             {deployment['deployment_status']}")
                
                if deployment.get('syncflow_deployment_id'):
                    print(f"SyncFlow ID:        {deployment['syncflow_deployment_id']}")
                    print(f"Deployed At:        {deployment.get('deployed_at', 'N/A')}")
                    print()
                    print("✅ Campaign is LIVE on SyncFlow!")
                elif deployment['deployment_status'] == 'safety_hold':
                    print()
                    print("⚠️  Auto-deploy skipped due to brand safety concerns")
                    print("   Review assets and manually deploy after approval")
                else:
                    print()
                    print("⚠️  Deployment to SyncFlow failed")
                    print("   Check SyncFlow service status")
                print()
                
                return deployment
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
        except httpx.ConnectError:
            print("❌ Error: Could not connect to SyncValue service")
            print(f"Ensure SyncValue is running on {SYNCVALUE_URL}")
        except Exception as e:
            print(f"❌ Error: {e}")


async def example_advantage_plus_info():
    """
    Example 3: Get Advantage+ Suite Information
    
    Shows how KIKI's agents map to Meta's Advantage+ features.
    """
    print("\n" + "=" * 80)
    print("Example 3: Advantage+ Suite Information")
    print("=" * 80)
    print()
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{SYNCVALUE_URL}/api/v1/advantage-plus-info")
            
            if response.status_code == 200:
                info = response.json()
                
                print("KIKI's Advantage+ Suite Enhancements")
                print()
                
                # Advantage+ Audience
                audience = info['advantage_plus_suite']['advantage_plus_audience']
                print(f"{'Advantage+ Audience':-^80}")
                print(f"Meta Feature:   {audience['meta_feature']}")
                print(f"KIKI Enhancement: {audience['kiki_enhancement']}")
                print(f"Agents:         {', '.join(audience['agents'])}")
                print(f"Advantage:      {audience['advantage']}")
                print()
                
                # Advantage+ Creative
                creative = info['advantage_plus_suite']['advantage_plus_creative']
                print(f"{'Advantage+ Creative':-^80}")
                print(f"Meta Feature:   {creative['meta_feature']}")
                print(f"KIKI Enhancement: {creative['kiki_enhancement']}")
                print(f"Agents:         {', '.join(creative['agents'])}")
                print(f"Advantage:      {creative['advantage']}")
                print()
                
                # Advantage+ Placements
                placements = info['advantage_plus_suite']['advantage_plus_placements']
                print(f"{'Advantage+ Placements':-^80}")
                print(f"Meta Feature:   {placements['meta_feature']}")
                print(f"KIKI Enhancement: {placements['kiki_enhancement']}")
                print(f"Agents:         {', '.join(placements['agents'])}")
                print(f"Advantage:      {placements['advantage']}")
                print()
                
                # Optimal Industries
                print(f"{'Optimal Industries for KIKI':-^80}")
                for industry in info['industry_targeting']['optimal_industries']:
                    print(f"\n{industry['name']}")
                    print(f"  Reason:        {industry['reason']}")
                    print(f"  Campaign Type: {industry['campaign_type']}")
                    print(f"  LTV Baseline:  {industry['ltv_baseline']}")
                print()
                
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")


async def example_multiple_urls():
    """
    Example 4: Batch Process Multiple URLs
    
    Demonstrates processing multiple business URLs in parallel
    to compare industry classifications and recommended strategies.
    """
    print("\n" + "=" * 80)
    print("Example 4: Batch URL-to-Campaign (Multiple Industries)")
    print("=" * 80)
    print()
    
    urls = [
        "https://www.nike.com",           # E-commerce (Fashion)
        "https://www.salesforce.com",     # SaaS (Enterprise B2B)
        "https://www.duolingo.com"        # Mobile App (Education)
    ]
    
    print(f"Processing {len(urls)} URLs in parallel...")
    print()
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        tasks = []
        for url in urls:
            task = client.post(
                f"{SYNCVALUE_URL}/api/v1/url-to-campaign",
                json={"url": url, "auto_deploy": False}
            )
            tasks.append(task)
        
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            print(f"{'Industry Classification Comparison':-^80}")
            print(f"{'URL':<35} {'Industry':<25} {'Campaign Type':<15}")
            print("-" * 80)
            
            for url, response in zip(urls, responses):
                if isinstance(response, Exception):
                    print(f"{url:<35} {'ERROR':<25} {'-':<15}")
                elif response.status_code == 200:
                    deployment = response.json()["deployment"]
                    industry = deployment["industry_category"]
                    campaign_type = deployment["campaign_type"]
                    ltv = deployment["ltv_baseline"]
                    
                    url_short = url.replace("https://www.", "").replace("https://", "")[:34]
                    print(f"{url_short:<35} {industry:<25} {campaign_type:<15} ${ltv:.0f}")
                else:
                    print(f"{url:<35} {'FAILED':<25} {'-':<15}")
            
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("KIKI Agent™ - Council of Nine: URL-to-Campaign Examples")
    print("=" * 80)
    print()
    print("These examples demonstrate the complete Advantage+ Suite:")
    print("• Industry classification from URL")
    print("• LTV baseline prediction")
    print("• Autonomous creative generation (5 ad copies + 3 image prompts)")
    print("• Brand safety validation")
    print("• Optional SyncFlow deployment with LTV constraints")
    print()
    print(f"Ensure SyncValue is running on {SYNCVALUE_URL}")
    print()
    
    try:
        # Example 1: Basic draft mode
        await example_url_to_campaign_basic()
        
        # Example 2: Auto-deploy mode
        # await example_url_to_campaign_auto_deploy()
        
        # Example 3: Get info about Advantage+ Suite
        await example_advantage_plus_info()
        
        # Example 4: Batch processing
        # await example_multiple_urls()
        
        print("=" * 80)
        print("✅ All examples completed!")
        print("=" * 80)
        print()
        print("Next Steps:")
        print("• Review the generated campaigns")
        print("• Customize ad copies and image prompts")
        print("• Deploy to SyncFlow when ready")
        print("• Monitor performance via SyncPortal dashboard")
        print()
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
