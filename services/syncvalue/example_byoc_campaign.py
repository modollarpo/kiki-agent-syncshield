#!/usr/bin/env python3
"""
BYOC (Bring Your Own Creative) Examples

Demonstrates how users can provide their own ad copies, images, videos,
and descriptions instead of relying entirely on AI generation.

This gives users full control over their campaign creatives while still
leveraging KIKI Agent's deployment and optimization capabilities.
"""

import asyncio
import sys
from pathlib import Path

# Add services to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.syncvalue.council_of_nine import CouncilOfNine


async def example_1_user_provided_ad_copies():
    """
    Example 1: User provides their own ad copies
    
    Use case: Marketing team has crafted specific messaging
    """
    print("=" * 80)
    print("EXAMPLE 1: User-Provided Ad Copies")
    print("=" * 80)
    
    council = CouncilOfNine()
    
    # User brings their own ad copies
    user_assets = {
        "ad_copies": [
            "🚀 Launch your SaaS product in 30 days, not 6 months",
            "Join 10,000+ founders who shipped faster with our platform",
            "Stop overthinking. Start building. Ship your MVP today.",
            "From idea to paying customers in one month - guaranteed",
            "The fastest way to validate your SaaS idea"
        ]
    }
    
    deployment = await council.prompt_to_campaign(
        prompt="Launch SaaS product for early-stage founders, $50k budget, target 4x ROI",
        auto_deploy=False,
        user_assets=user_assets
    )
    
    print(f"\n📊 Campaign: {deployment.deployment_id}")
    print(f"💰 Budget: ${deployment.budget:,.0f}")
    print(f"🎯 Target ROI: {deployment.target_roi}x")
    print(f"📦 Asset Source: {deployment.assets_source}")
    print(f"\n✍️ Ad Copies (User-Provided):")
    for i, copy in enumerate(deployment.user_provided_ad_copies, 1):
        print(f"  {i}. {copy}")
    
    print(f"\n🖼️ Image Prompts (AI-Generated): {len(deployment.image_prompts)}")
    for i, prompt in enumerate(deployment.image_prompts, 1):
        print(f"  {i}. {prompt[:80]}...")


async def example_2_user_provided_images():
    """
    Example 2: User provides their own product images
    
    Use case: Professional photoshoot already completed
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: User-Provided Product Images")
    print("=" * 80)
    
    council = CouncilOfNine()
    
    # User has professional product photos
    user_assets = {
        "images": [
            "https://cdn.myshop.com/product-hero-shot.jpg",
            "https://cdn.myshop.com/lifestyle-image.jpg",
            "https://cdn.myshop.com/detail-close-up.jpg"
        ],
        "descriptions": [
            "Hero shot: Product on white background, studio lighting",
            "Lifestyle: Customer using product in modern home setting",
            "Close-up: Premium materials and craftsmanship detail"
        ]
    }
    
    deployment = await council.url_to_campaign(
        url="https://luxurywatches.example.com",
        auto_deploy=False,
        user_assets=user_assets
    )
    
    print(f"\n📊 Campaign: {deployment.deployment_id}")
    print(f"🏢 Brand: {deployment.brand_name}")
    print(f"📦 Asset Source: {deployment.assets_source}")
    
    print(f"\n🖼️ Images (User-Provided):")
    for i, (img, desc) in enumerate(zip(deployment.user_provided_images, deployment.user_provided_descriptions), 1):
        print(f"  {i}. {img}")
        print(f"     → {desc}")
    
    print(f"\n✍️ Ad Copies (AI-Generated): {len(deployment.ad_copies)}")
    for i, copy in enumerate(deployment.ad_copies[:2], 1):
        print(f"  {i}. {copy}")


async def example_3_hybrid_approach():
    """
    Example 3: Mix user-provided and AI-generated assets
    
    Use case: User has some assets but wants AI to fill gaps
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Hybrid Approach (User + AI)")
    print("=" * 80)
    
    council = CouncilOfNine()
    
    # User provides hero image and 2 ad copies, AI generates the rest
    user_assets = {
        "images": [
            "https://s3.amazonaws.com/mybrand/hero-image-q4.jpg"
        ],
        "ad_copies": [
            "🎮 The most immersive mobile game of 2026",
            "Join 5M players worldwide - Download free today"
        ]
    }
    
    deployment = await council.prompt_to_campaign(
        prompt="Launch mobile game for casual players, $100k budget",
        auto_deploy=False,
        user_assets=user_assets
    )
    
    print(f"\n📊 Campaign: {deployment.deployment_id}")
    print(f"📦 Asset Source: {deployment.assets_source}")
    
    print(f"\n✍️ Ad Copies:")
    print(f"  User-Provided: {len(deployment.user_provided_ad_copies)}")
    for copy in deployment.user_provided_ad_copies:
        print(f"    → {copy}")
    print(f"  AI-Generated: {len(deployment.ad_copies)}")
    for copy in deployment.ad_copies[:2]:
        print(f"    → {copy}")
    
    print(f"\n🖼️ Images:")
    print(f"  User-Provided: {len(deployment.user_provided_images)}")
    print(f"  AI-Generated: {len(deployment.image_prompts)}")


async def example_4_user_provided_video():
    """
    Example 4: User provides their own video content
    
    Use case: Brand has existing video assets from production
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: User-Provided Video Content")
    print("=" * 80)
    
    council = CouncilOfNine()
    
    # User has professionally produced videos
    user_assets = {
        "videos": [
            "https://vimeo.com/mybrand/product-demo-30s",
            "https://vimeo.com/mybrand/customer-testimonial-15s"
        ],
        "descriptions": [
            "30-second product demonstration showing key features",
            "15-second customer testimonial from enterprise client"
        ]
    }
    
    deployment = await council.url_to_campaign(
        url="https://enterprise-saas.example.com",
        auto_deploy=False,
        user_assets=user_assets
    )
    
    print(f"\n📊 Campaign: {deployment.deployment_id}")
    print(f"🏢 Brand: {deployment.brand_name}")
    print(f"📦 Asset Source: {deployment.assets_source}")
    
    print(f"\n🎥 Videos (User-Provided):")
    for i, (video, desc) in enumerate(zip(deployment.user_provided_videos, deployment.user_provided_descriptions), 1):
        print(f"  {i}. {video}")
        print(f"     → {desc}")
    
    print(f"\n✍️ Ad Copies (AI-Generated): {len(deployment.ad_copies)}")
    for i, copy in enumerate(deployment.ad_copies[:3], 1):
        print(f"  {i}. {copy}")


async def example_5_complete_byoc():
    """
    Example 5: User provides all creative assets
    
    Use case: Agency has complete creative package, just needs deployment
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Complete BYOC (All Assets User-Provided)")
    print("=" * 80)
    
    council = CouncilOfNine()
    
    # User provides everything - KIKI just handles deployment & optimization
    user_assets = {
        "ad_copies": [
            "Limited Time: 50% Off Premium Membership",
            "Join 100K+ professionals advancing their careers",
            "Get certified in 30 days with our proven system"
        ],
        "images": [
            "https://cdn.edtech.com/hero-campaign-q1.jpg",
            "https://cdn.edtech.com/social-proof-badges.jpg"
        ],
        "videos": [
            "https://youtube.com/watch?v=abc123_campaign_video"
        ],
        "descriptions": [
            "Hero image: Modern professional at laptop with certification badge overlay",
            "Social proof: Logos of 500+ top companies hiring our graduates",
            "Video: 60-second student success story montage"
        ]
    }
    
    deployment = await council.prompt_to_campaign(
        prompt="EdTech platform, B2B professional training, $200k budget, 5x ROI target",
        auto_deploy=False,
        user_assets=user_assets
    )
    
    print(f"\n📊 Campaign: {deployment.deployment_id}")
    print(f"💰 Budget: ${deployment.budget:,.0f}")
    print(f"🎯 Target ROI: {deployment.target_roi}x")
    print(f"💵 Max CPA: ${deployment.max_cpa:.2f}")
    print(f"📦 Asset Source: {deployment.assets_source}")
    
    print(f"\n📦 All Assets User-Provided:")
    print(f"  ✍️  Ad Copies: {len(deployment.user_provided_ad_copies)}")
    print(f"  🖼️  Images: {len(deployment.user_provided_images)}")
    print(f"  🎥 Videos: {len(deployment.user_provided_videos)}")
    print(f"  📝 Descriptions: {len(deployment.user_provided_descriptions)}")
    
    print(f"\n✅ KIKI Agent handles:")
    print(f"  • LTV prediction and max CPA calculation")
    print(f"  • Brand safety validation")
    print(f"  • Campaign deployment optimization")
    print(f"  • Real-time bidding with LTV constraints")
    print(f"  • Performance tracking and attribution")


async def main():
    """Run all BYOC examples"""
    try:
        await example_1_user_provided_ad_copies()
        await example_2_user_provided_images()
        await example_3_hybrid_approach()
        await example_4_user_provided_video()
        await example_5_complete_byoc()
        
        print("\n" + "=" * 80)
        print("✅ All BYOC examples completed successfully!")
        print("=" * 80)
        
        print("\n💡 Key Takeaways:")
        print("  1. Users can provide ANY combination of creatives")
        print("  2. AI generates only what's missing (hybrid approach)")
        print("  3. Asset source is tracked: 'generated', 'user_provided', or 'hybrid'")
        print("  4. KIKI still handles optimization, safety, and deployment")
        print("  5. Full flexibility: AI-first, user-first, or mixed workflows")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
