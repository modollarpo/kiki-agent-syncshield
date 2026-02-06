"""
Example: Prompt-to-Campaign Automation

Demonstrates how to use KIKI Agent's Council of Nine to transform
natural language prompts into complete advertising campaigns.

This is the PRIMARY entry point for users who want to describe their
campaign goals without needing a website URL.

Usage:
    python example_prompt_to_campaign.py
"""

import asyncio
import httpx
import json
from typing import Dict, Any


# Configuration
SYNCVALUE_URL = "http://localhost:8002"


async def prompt_to_campaign(
    prompt: str,
    auto_deploy: bool = False
) -> Dict[str, Any]:
    """
    Call the Council of Nine Prompt-to-Campaign API.
    
    Args:
        prompt: Natural language campaign description
        auto_deploy: Whether to automatically deploy to SyncFlow
        
    Returns:
        Complete campaign deployment result
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{SYNCVALUE_URL}/api/v1/prompt-to-campaign",
            json={
                "prompt": prompt,
                "auto_deploy": auto_deploy
            }
        )
        response.raise_for_status()
        return response.json()


def print_campaign_summary(result: Dict[str, Any]):
    """Print formatted campaign summary"""
    deployment = result.get("deployment", {})
    financial = result.get("financial_summary", {})
    
    print("\n" + "="*80)
    print("🎯 CAMPAIGN DEPLOYMENT SUMMARY")
    print("="*80)
    
    print(f"\n📊 CAMPAIGN DETAILS:")
    print(f"   Deployment ID:  {deployment.get('deployment_id')}")
    print(f"   Brand Name:     {deployment.get('brand_name')}")
    print(f"   Industry:       {deployment.get('industry_category')}")
    print(f"   Campaign Type:  {deployment.get('campaign_type')}")
    print(f"   Status:         {deployment.get('deployment_status')}")
    
    print(f"\n💰 FINANCIAL CONSTRAINTS:")
    if financial.get('budget'):
        print(f"   Budget:         ${financial['budget']:,.0f}")
    if financial.get('target_roi'):
        print(f"   Target ROI:     {financial['target_roi']}x")
    print(f"   LTV Baseline:   ${financial.get('ltv_baseline', 0):.2f}")
    if financial.get('max_cpa'):
        print(f"   Max CPA:        ${financial['max_cpa']:.2f}")
        print(f"   ROI Formula:    {financial.get('roi_calculation')}")
    
    print(f"\n🎨 GENERATED ASSETS:")
    ad_copies = deployment.get('ad_copies', [])
    image_prompts = deployment.get('image_prompts', [])
    
    print(f"\n   {len(ad_copies)} Ad Copy Variations:")
    for i, copy in enumerate(ad_copies[:3], 1):  # Show first 3
        print(f"   {i}. \"{copy}\"")
    if len(ad_copies) > 3:
        print(f"   ... and {len(ad_copies) - 3} more")
    
    print(f"\n   {len(image_prompts)} Image Prompt Variations:")
    for i, prompt in enumerate(image_prompts, 1):
        print(f"   {i}. \"{prompt[:80]}...\"" if len(prompt) > 80 else f"   {i}. \"{prompt}\"")
    
    print(f"\n🛡️ SAFETY & COMPLIANCE:")
    print(f"   Brand Safe:     {'✅ YES' if deployment.get('brand_safe') else '⚠️ REVIEW REQUIRED'}")
    print(f"   Compliance:     {deployment.get('compliance_status')}")
    
    if deployment.get('syncflow_deployment_id'):
        print(f"\n🚀 DEPLOYMENT:")
        print(f"   SyncFlow ID:    {deployment['syncflow_deployment_id']}")
        print(f"   Deployed At:    {deployment.get('deployed_at')}")
    
    print("\n" + "="*80 + "\n")


async def example_1_budget_roi():
    """
    Example 1: Launch with Budget and ROI Target
    
    Prompt: "Launch product with $100k budget, target ROI 3x"
    """
    print("\n" + "🚀 "*20)
    print("EXAMPLE 1: Budget + ROI Target Campaign")
    print("🚀 "*20)
    
    prompt = "Launch product with $100k budget, target ROI 3x"
    print(f"\nPrompt: \"{prompt}\"")
    print("\n⏳ Generating campaign (this may take 30-60 seconds)...")
    
    result = await prompt_to_campaign(
        prompt=prompt,
        auto_deploy=False  # Draft mode - review before deploying
    )
    
    print_campaign_summary(result)
    
    # Explain the ROI calculation
    financial = result.get("financial_summary", {})
    if financial.get('max_cpa'):
        print("💡 INSIGHTS:")
        print(f"   To achieve 3x ROI with LTV ${financial['ltv_baseline']:.2f}:")
        print(f"   → Maximum CPA must be ${financial['max_cpa']:.2f}")
        print(f"   → SyncFlow will enforce this constraint in real-time bidding")
        print(f"   → Budget of ${financial['budget']:,.0f} will be allocated optimally")


async def example_2_saas_b2b():
    """
    Example 2: SaaS B2B Enterprise Campaign
    
    Prompt: "Create campaign for SaaS startup, B2B enterprise audience, $50k budget"
    """
    print("\n" + "🚀 "*20)
    print("EXAMPLE 2: SaaS B2B Enterprise Campaign")
    print("🚀 "*20)
    
    prompt = "Create campaign for SaaS startup, B2B enterprise audience, $50k budget"
    print(f"\nPrompt: \"{prompt}\"")
    print("\n⏳ Generating campaign...")
    
    result = await prompt_to_campaign(
        prompt=prompt,
        auto_deploy=False
    )
    
    print_campaign_summary(result)
    
    print("💡 INSIGHTS:")
    print("   B2B campaigns typically have:")
    print("   → Higher LTV (often $800-$2,500)")
    print("   → Longer sales cycles")
    print("   → More complex buyer journeys")
    print("   → SyncBrain generates ALC (App-Like Conversions) campaigns")


async def example_3_mobile_game():
    """
    Example 3: Mobile Game Launch
    
    Prompt: "Mobile game launch, casual players, $25k budget, ROI 2.5x"
    """
    print("\n" + "🚀 "*20)
    print("EXAMPLE 3: Mobile Game Launch")
    print("🚀 "*20)
    
    prompt = "Mobile game launch, casual players, $25k budget, ROI 2.5x"
    print(f"\nPrompt: \"{prompt}\"")
    print("\n⏳ Generating campaign...")
    
    result = await prompt_to_campaign(
        prompt=prompt,
        auto_deploy=False
    )
    
    print_campaign_summary(result)
    
    print("💡 INSIGHTS:")
    print("   Mobile gaming campaigns:")
    print("   → Lower LTV (typically $25-$100)")
    print("   → High volume strategy")
    print("   → Focus on install-to-purchase funnel")
    print("   → SyncCreate generates playful, engaging creative")


async def example_4_auto_deploy():
    """
    Example 4: Auto-Deploy Campaign
    
    Demonstrates automatic deployment to SyncFlow when brand safety passes.
    """
    print("\n" + "🚀 "*20)
    print("EXAMPLE 4: Auto-Deploy Mode")
    print("🚀 "*20)
    
    prompt = "E-commerce store for organic skincare, target millennials, $40k budget"
    print(f"\nPrompt: \"{prompt}\"")
    print("\n⏳ Generating and auto-deploying campaign...")
    
    result = await prompt_to_campaign(
        prompt=prompt,
        auto_deploy=True  # Auto-deploy if brand safe
    )
    
    print_campaign_summary(result)
    
    deployment = result.get("deployment", {})
    if deployment.get('deployment_status') == 'deployed':
        print("✅ SUCCESS: Campaign automatically deployed to SyncFlow!")
        print("   → Monitor performance in SyncPortal dashboard")
        print("   → SyncFlow is now bidding with LTV constraints")
        print("   → SyncEngage will trigger retention campaigns")
    elif deployment.get('deployment_status') == 'safety_hold':
        print("⚠️  SAFETY HOLD: Campaign not deployed due to brand safety concerns")
        print("   → Review flagged content manually")
        print("   → Fix issues and redeploy")


async def example_5_batch_campaigns():
    """
    Example 5: Batch Campaign Generation
    
    Generate multiple campaigns from different prompts.
    """
    print("\n" + "🚀 "*20)
    print("EXAMPLE 5: Batch Campaign Generation")
    print("🚀 "*20)
    
    prompts = [
        "SaaS CRM tool, small business owners, $30k budget",
        "Online course platform, students and professionals, $20k budget, ROI 4x",
        "Fitness app subscription, health enthusiasts, $35k budget"
    ]
    
    print(f"\nGenerating {len(prompts)} campaigns...")
    
    campaigns = []
    for i, prompt in enumerate(prompts, 1):
        print(f"\n[{i}/{len(prompts)}] Processing: \"{prompt}\"")
        result = await prompt_to_campaign(prompt, auto_deploy=False)
        campaigns.append(result)
        print(f"    ✅ Complete: {result['deployment']['brand_name']}")
    
    print("\n" + "="*80)
    print("📊 BATCH SUMMARY")
    print("="*80)
    
    for i, campaign in enumerate(campaigns, 1):
        deployment = campaign['deployment']
        financial = campaign['financial_summary']
        print(f"\n{i}. {deployment['brand_name']}")
        print(f"   Industry: {deployment['industry_category']}")
        if financial.get('budget'):
            print(f"   Budget: ${financial['budget']:,.0f}")
        print(f"   LTV: ${financial['ltv_baseline']:.2f}")
        if financial.get('max_cpa'):
            print(f"   Max CPA: ${financial['max_cpa']:.2f}")
        print(f"   Status: {deployment['deployment_status']}")


async def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("KIKI Agent™ - Prompt-to-Campaign Examples")
    print("Council of Nine Orchestration Demo")
    print("="*80)
    
    print("\nThese examples demonstrate the PRIMARY entry point for KIKI Agent:")
    print("Transform natural language prompts into complete advertising campaigns.\n")
    
    try:
        # Run examples sequentially
        await example_1_budget_roi()
        
        # Uncomment to run more examples:
        # await example_2_saas_b2b()
        # await example_3_mobile_game()
        # await example_4_auto_deploy()
        # await example_5_batch_campaigns()
        
        print("\n✅ All examples completed successfully!")
        print("\n🎯 Next Steps:")
        print("   1. Review the generated campaigns above")
        print("   2. Try your own prompts with the /api/v1/prompt-to-campaign endpoint")
        print("   3. Use auto_deploy=true to deploy to SyncFlow automatically")
        print("   4. Monitor campaign performance in SyncPortal dashboard")
        
    except httpx.ConnectError:
        print("\n❌ ERROR: Cannot connect to SyncValue service")
        print("   Make sure SyncValue is running on http://localhost:8002")
        print("\n   Start it with:")
        print("   $ python services/syncvalue/app/main.py")
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
