"""
Council of Nine - URL-to-Campaign Orchestrator

The strategic nerve center of KIKI Agent™ that coordinates all services
to transform a URL or prompt into a complete, deployed advertising campaign.

This module implements the "Advantage+ Suite" - Meta's automation features
enhanced with LTV prediction, brand safety, and autonomous creative generation.

Architecture: Service Orchestrator Pattern
Coordinates: SyncValue, SyncBrain, SyncCreate, SyncShield, SyncFlow, SyncEngage
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import httpx
import json

# Setup logging
logger = logging.getLogger("council_of_nine")
logging.basicConfig(level=logging.INFO)


# ============================================================================
# Domain Models
# ============================================================================

@dataclass
class CampaignDeployment:
    """Complete campaign deployment result"""
    deployment_id: str
    url: Optional[str]  # Optional for prompt-based campaigns
    brand_name: str
    industry_category: str
    campaign_type: str  # ASC or ALC
    ltv_baseline: float
    
    # Budget and ROI constraints (for prompt-based campaigns)
    budget: Optional[float] = None
    target_roi: Optional[float] = None
    max_cpa: Optional[float] = None  # Calculated from LTV and target ROI
    
    # Generated assets
    ad_copies: List[str] = field(default_factory=list)
    image_prompts: List[str] = field(default_factory=list)
    video_prompts: List[str] = field(default_factory=list)  # For video campaigns
    
    # User-provided assets (BYOC - Bring Your Own Creative)
    user_provided_ad_copies: List[str] = field(default_factory=list)
    user_provided_images: List[str] = field(default_factory=list)  # URLs or base64
    user_provided_videos: List[str] = field(default_factory=list)  # URLs or file paths
    user_provided_descriptions: List[str] = field(default_factory=list)
    
    # Asset source tracking
    assets_source: str = "generated"  # "generated", "user_provided", or "hybrid"
    
    # Safety and compliance
    brand_safe: bool = False
    compliance_status: str = "pending"
    
    # Deployment status
    syncflow_deployment_id: Optional[str] = None
    deployment_status: str = "draft"  # draft, deployed, active, paused
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    deployed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "deployment_id": self.deployment_id,
            "url": self.url,
            "brand_name": self.brand_name,
            "industry_category": self.industry_category,
            "campaign_type": self.campaign_type,
            "ltv_baseline": self.ltv_baseline,
            "budget": self.budget,
            "target_roi": self.target_roi,
            "max_cpa": self.max_cpa,
            "ad_copies": self.ad_copies,
            "image_prompts": self.image_prompts,
            "video_prompts": self.video_prompts,
            "user_provided_ad_copies": self.user_provided_ad_copies,
            "user_provided_images": self.user_provided_images,
            "user_provided_videos": self.user_provided_videos,
            "user_provided_descriptions": self.user_provided_descriptions,
            "assets_source": self.assets_source,
            "brand_safe": self.brand_safe,
            "compliance_status": self.compliance_status,
            "syncflow_deployment_id": self.syncflow_deployment_id,
            "deployment_status": self.deployment_status,
            "created_at": self.created_at.isoformat(),
            "deployed_at": self.deployed_at.isoformat() if self.deployed_at else None
        }


# ============================================================================
# Service Clients
# ============================================================================

class SyncValueClient:
    """Client for SyncValue - LTV prediction and brand extraction"""
    
    def __init__(self, base_url: str = "http://syncvalue:8002"):
        self.base_url = base_url
    
    async def scrape_and_classify(self, url: str) -> Dict[str, Any]:
        """Scrape URL and get industry classification"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/scrape-and-generate",
                json={"url": url}
            )
            response.raise_for_status()
            return response.json()


class SyncBrainClient:
    """Client for SyncBrain - Strategic planning and LLM orchestration"""
    
    def __init__(self, base_url: str = "http://syncbrain:8001"):
        self.base_url = base_url
    
    async def parse_campaign_prompt(self, prompt: str) -> Dict[str, Any]:
        """Parse natural language campaign prompt into structured data"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/parse-prompt",
                json={"prompt": prompt}
            )
            response.raise_for_status()
            return response.json()
    
    async def plan_campaign_strategy(self, brand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate campaign strategy based on brand and industry"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/plan-strategy",
                json={
                    "brand_name": brand_data.get("brand_name"),
                    "industry": brand_data.get("industry_profile", {}).get("category"),
                    "campaign_type": brand_data.get("industry_profile", {}).get("campaign_type"),
                    "context": brand_data
                }
            )
            response.raise_for_status()
            return response.json()


class SyncCreateClient:
    """Client for SyncCreate - Creative generation with Stable Diffusion"""
    
    def __init__(self, base_url: str = "http://synccreate:8004"):
        self.base_url = base_url
    
    async def generate_ad_copies(
        self, 
        brand_name: str, 
        campaign_brief: Dict[str, Any],
        count: int = 5
    ) -> List[str]:
        """Generate ad copy variations"""
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                f"{self.base_url}/generate-copy",
                json={
                    "brand_name": brand_name,
                    "campaign_brief": campaign_brief,
                    "count": count
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("ad_copies", [])
    
    async def generate_image_prompts(
        self, 
        brand_data: Dict[str, Any],
        count: int = 3
    ) -> List[str]:
        """Generate image prompts for Stable Diffusion"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/generate-image-prompts",
                json={
                    "brand_data": brand_data,
                    "count": count
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("image_prompts", [])
    
    async def generate_video_prompts(
        self, 
        brand_data: Dict[str, Any],
        count: int = 2
    ) -> List[str]:
        """Generate video prompts for video generation models (RunwayML, DeepBrain, etc.)"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/generate-video-prompts",
                json={
                    "brand_data": brand_data,
                    "count": count
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("video_prompts", [])


class SyncShieldClient:
    """Client for SyncShield - Brand safety and compliance"""
    
    def __init__(self, base_url: str = "http://syncshield:8006"):
        self.base_url = base_url
    
    async def validate_brand_safety(
        self, 
        ad_copies: List[str],
        brand_name: str
    ) -> Dict[str, Any]:
        """Validate ad copies for brand safety"""
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{self.base_url}/validate",
                json={
                    "content": ad_copies,
                    "brand_name": brand_name,
                    "check_type": "brand_safety"
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def log_campaign_deployment(
        self, 
        deployment_data: Dict[str, Any]
    ) -> bool:
        """Log campaign deployment for audit trail"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/audit",
                    json={
                        "event": "campaign_deployed",
                        "data": deployment_data
                    }
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to log to SyncShield: {e}")
            return False


class SyncFlowClient:
    """Client for SyncFlow - Real-time bidding and deployment"""
    
    def __init__(self, base_url: str = "http://syncflow:8003"):
        self.base_url = base_url
    
    async def deploy_campaign(
        self,
        campaign_data: Dict[str, Any],
        ltv_constraint: float
    ) -> Dict[str, Any]:
        """Deploy campaign with LTV-based bidding constraints"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/deploy-campaign",
                json={
                    "campaign_data": campaign_data,
                    "ltv_constraint": ltv_constraint,
                    "bid_strategy": "ltv_optimized"
                }
            )
            response.raise_for_status()
            return response.json()


# ============================================================================
# Council of Nine Orchestrator
# ============================================================================

class CouncilOfNine:
    """
    Central orchestrator for URL-to-Campaign automation.
    
    Orchestrates the complete flow:
    1. SyncValue: Scrape URL + Classify Industry + Predict LTV
    2. SyncBrain: Generate Campaign Strategy
    3. SyncCreate: Generate Ad Copies + Image Prompts
    4. SyncShield: Validate Brand Safety + Compliance
    5. SyncFlow: Deploy Campaign with LTV Constraints
    6. SyncEngage: Setup retention triggers (future)
    """
    
    def __init__(
        self,
        syncvalue_url: str = "http://syncvalue:8002",
        syncbrain_url: str = "http://syncbrain:8001",
        synccreate_url: str = "http://synccreate:8004",
        syncshield_url: str = "http://syncshield:8006",
        syncflow_url: str = "http://syncflow:8003"
    ):
        self.syncvalue = SyncValueClient(syncvalue_url)
        self.syncbrain = SyncBrainClient(syncbrain_url)
        self.synccreate = SyncCreateClient(synccreate_url)
        self.syncshield = SyncShieldClient(syncshield_url)
        self.syncflow = SyncFlowClient(syncflow_url)
    
    async def url_to_campaign(
        self,
        url: str,
        auto_deploy: bool = False,
        user_assets: Optional[Dict[str, Any]] = None
    ) -> CampaignDeployment:
        """
        Transform a URL into a complete advertising campaign.
        
        This is the main "Advantage+ Suite" workflow:
        - Advantage+ Audience → SyncValue LTV prediction
        - Advantage+ Creative → SyncCreate autonomous generation
        - Advantage+ Placements → SyncFlow LTV-optimized bidding
        
        Args:
            url: Target business website URL
            auto_deploy: Whether to automatically deploy to SyncFlow
            user_assets: Optional dict with user-provided creatives:
                {
                    "ad_copies": ["Custom ad text 1", "Custom ad text 2"],
                    "images": ["https://cdn.example.com/img1.jpg", "base64data..."],
                    "videos": ["https://cdn.example.com/video1.mp4"],
                    "descriptions": ["Product description for ad"]
                }
            
        Returns:
            CampaignDeployment with generated and/or user-provided assets
        """
        import uuid
        deployment_id = f"campaign_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"🚀 Council of Nine: Starting URL-to-Campaign for {url}")
        logger.info(f"Deployment ID: {deployment_id}")
        
        # ====================================================================
        # PHASE 1: Discovery & Analysis (SyncValue)
        # ====================================================================
        logger.info("📊 PHASE 1: Brand extraction and industry classification...")
        
        try:
            brand_data = await self.syncvalue.scrape_and_classify(url)
        except Exception as e:
            logger.error(f"SyncValue extraction failed: {e}")
            raise RuntimeError(f"Failed to extract brand data from URL: {e}")
        
        brand_name = brand_data.get("brand_identity", {}).get("brand_name", "Unknown Brand")
        industry_profile = brand_data.get("brand_identity", {}).get("industry_profile", {})
        
        logger.info(f"✅ Brand: {brand_name}")
        logger.info(f"✅ Industry: {industry_profile.get('category', 'Unknown')}")
        logger.info(f"✅ Campaign Type: {industry_profile.get('campaign_type', 'ASC')}")
        logger.info(f"✅ LTV Baseline: ${industry_profile.get('ltv_baseline', 0):.2f}")
        
        # ====================================================================
        # PHASE 2: Strategic Planning (SyncBrain)
        # ====================================================================
        logger.info("🧠 PHASE 2: Generating campaign strategy...")
        
        try:
            campaign_strategy = await self.syncbrain.plan_campaign_strategy(brand_data.get("brand_identity", {}))
        except Exception as e:
            logger.warning(f"SyncBrain strategy generation failed: {e}. Using fallback.")
            campaign_strategy = {
                "target_audience": "General audience interested in " + industry_profile.get('category', 'products'),
                "key_message": f"Discover {brand_name}",
                "tone": brand_data.get("brand_identity", {}).get("tone", "professional")
            }
        
        logger.info(f"✅ Target Audience: {campaign_strategy.get('target_audience')}")
        logger.info(f"✅ Key Message: {campaign_strategy.get('key_message')}")
        
        # ====================================================================
        # PHASE 3: Creative Generation (SyncCreate or User-Provided)
        # ====================================================================
        logger.info("🎨 PHASE 3: Processing ad creatives...")
        
        # Check for user-provided assets (BYOC - Bring Your Own Creative)
        user_ad_copies = user_assets.get("ad_copies", []) if user_assets else []
        user_images = user_assets.get("images", []) if user_assets else []
        user_videos = user_assets.get("videos", []) if user_assets else []
        user_descriptions = user_assets.get("descriptions", []) if user_assets else []
        
        has_user_content = any([user_ad_copies, user_images, user_videos, user_descriptions])
        
        if has_user_content:
            logger.info(f"📦 User provided: {len(user_ad_copies)} ad copies, {len(user_images)} images, {len(user_videos)} videos")
        
        try:
            # Generate ad copies (only if not provided by user)
            if user_ad_copies:
                ad_copies = []
                logger.info("⏭️  Skipping ad copy generation (user-provided)")
            else:
                ad_copies = await self.synccreate.generate_ad_copies(
                    brand_name=brand_name,
                    campaign_brief=campaign_strategy,
                    count=5
                )
                logger.info(f"✅ Generated {len(ad_copies)} ad copy variations")
            
            # Generate image prompts (only if not provided by user)
            if user_images:
                image_prompts = []
                logger.info("⏭️  Skipping image generation (user-provided)")
            else:
                image_prompts = await self.synccreate.generate_image_prompts(
                    brand_data=brand_data.get("brand_identity", {}),
                    count=3
                )
                logger.info(f"✅ Generated {len(image_prompts)} image prompts")
            
            # Generate video prompts (only if not provided by user)
            if user_videos:
                video_prompts = []
                logger.info("⏭️  Skipping video generation (user-provided)")
            else:
                video_prompts = await self.synccreate.generate_video_prompts(
                    brand_data=brand_data.get("brand_identity", {}),
                    count=2
                )
                logger.info(f"✅ Generated {len(video_prompts)} video prompts")
            
        except Exception as e:
            logger.warning(f"SyncCreate generation failed: {e}. Using placeholder assets.")
            ad_copies = [
                f"Discover {brand_name} - Transform your experience",
                f"{brand_name}: Quality you can trust",
                f"Join thousands who love {brand_name}",
                f"Experience the {brand_name} difference today",
                f"Shop {brand_name} - Limited time offer"
            ]
            image_prompts = [
                f"Professional product shot of {brand_name} products, clean background, studio lighting",
                f"{brand_name} lifestyle image, happy customers, modern aesthetic",
                f"Abstract brand identity for {brand_name}, vibrant colors, minimalist design"
            ]
            video_prompts = [
                f"{brand_name} product showcase video, smooth camera movement, professional lighting",
                f"{brand_name} customer testimonial montage, authentic stories, cinematic quality"
            ]
        
        # ====================================================================
        # PHASE 4: Brand Safety & Compliance (SyncShield)
        # ====================================================================
        logger.info("🛡️ PHASE 4: Validating brand safety and compliance...")
        
        try:
            safety_check = await self.syncshield.validate_brand_safety(
                ad_copies=ad_copies,
                brand_name=brand_name
            )
            brand_safe = safety_check.get("all_safe", True)
            compliance_status = "approved" if brand_safe else "review_required"
            logger.info(f"✅ Brand Safety: {'PASS' if brand_safe else 'REVIEW REQUIRED'}")
        except Exception as e:
            logger.warning(f"SyncShield validation failed: {e}. Proceeding with caution.")
            brand_safe = False
            compliance_status = "validation_failed"
        
        # ====================================================================
        # Create Deployment Object
        # ====================================================================
        # Determine asset source
        if has_user_content and (ad_copies or image_prompts or video_prompts):
            assets_source = "hybrid"  # Mix of user-provided and generated
        elif has_user_content:
            assets_source = "user_provided"  # All user-provided
        else:
            assets_source = "generated"  # All AI-generated
        
        deployment = CampaignDeployment(
            deployment_id=deployment_id,
            url=url,
            brand_name=brand_name,
            industry_category=industry_profile.get("category", "General"),
            campaign_type=industry_profile.get("campaign_type", "ASC"),
            ltv_baseline=industry_profile.get("ltv_baseline", 50.0),
            ad_copies=ad_copies,
            image_prompts=image_prompts,
            video_prompts=video_prompts,
            user_provided_ad_copies=user_ad_copies,
            user_provided_images=user_images,
            user_provided_videos=user_videos,
            user_provided_descriptions=user_descriptions,
            assets_source=assets_source,
            brand_safe=brand_safe,
            compliance_status=compliance_status,
            deployment_status="draft"
        )
        
        # ====================================================================
        # PHASE 5: Campaign Deployment (SyncFlow) - Optional
        # ====================================================================
        if auto_deploy and brand_safe:
            logger.info("🚀 PHASE 5: Deploying campaign to SyncFlow...")
            
            try:
                deployment_result = await self.syncflow.deploy_campaign(
                    campaign_data={
                        "brand_name": brand_name,
                        "ad_copies": ad_copies,
                        "image_prompts": image_prompts,
                        "campaign_type": industry_profile.get("campaign_type"),
                        "target_audience": campaign_strategy.get("target_audience")
                    },
                    ltv_constraint=industry_profile.get("ltv_baseline", 50.0)
                )
                
                deployment.syncflow_deployment_id = deployment_result.get("deployment_id")
                deployment.deployment_status = "deployed"
                deployment.deployed_at = datetime.utcnow()
                
                logger.info(f"✅ Deployed to SyncFlow: {deployment.syncflow_deployment_id}")
            except Exception as e:
                logger.error(f"SyncFlow deployment failed: {e}")
                deployment.deployment_status = "deployment_failed"
        elif auto_deploy and not brand_safe:
            logger.warning("⚠️ Auto-deploy skipped due to brand safety concerns")
            deployment.deployment_status = "safety_hold"
        
        # ====================================================================
        # PHASE 6: Audit Logging (SyncShield)
        # ====================================================================
        logger.info("📝 PHASE 6: Logging campaign deployment...")
        
        await self.syncshield.log_campaign_deployment(deployment.to_dict())
        
        # ====================================================================
        # Complete
        # ====================================================================
        logger.info(f"✅ Council of Nine: Campaign creation complete!")
        logger.info(f"📊 Status: {deployment.deployment_status}")
        logger.info(f"🎯 Assets: {len(ad_copies)} ad copies, {len(image_prompts)} image prompts, {len(video_prompts)} video prompts")
        
        return deployment
    
    async def prompt_to_campaign(
        self,
        prompt: str,
        auto_deploy: bool = False,
        user_assets: Optional[Dict[str, Any]] = None
    ) -> CampaignDeployment:
        """
        Generate campaign from a text prompt.
        
        Handles prompts like:
        - "Launch product with $100k budget, target ROI 3x"
        - "Create campaign for SaaS startup, B2B enterprise audience"
        - "Mobile game launch, casual players, $50k budget"
        
        Uses SyncBrain to interpret the prompt and generate campaign assets
        without requiring a URL.
        
        Args:
            prompt: Natural language campaign description
            auto_deploy: Whether to automatically deploy to SyncFlow
            user_assets: Optional dict with user-provided creatives (see url_to_campaign)
            
        Returns:
            CampaignDeployment with generated and/or user-provided assets
        """
        import uuid
        deployment_id = f"prompt_campaign_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"🚀 Council of Nine: Prompt-to-Campaign")
        logger.info(f"Deployment ID: {deployment_id}")
        logger.info(f"Prompt: {prompt}")
        
        # ====================================================================
        # PHASE 1: Parse & Interpret Prompt (SyncBrain)
        # ====================================================================
        logger.info("🧠 PHASE 1: Parsing campaign prompt...")
        
        try:
            parsed_prompt = await self.syncbrain.parse_campaign_prompt(prompt)
        except Exception as e:
            logger.warning(f"SyncBrain prompt parsing failed: {e}. Using fallback parser.")
            # Fallback: Simple keyword extraction
            parsed_prompt = self._fallback_parse_prompt(prompt)
        
        brand_name = parsed_prompt.get("brand_name", "New Product Launch")
        industry = parsed_prompt.get("industry", "General")
        audience = parsed_prompt.get("target_audience", "Broad audience")
        budget = parsed_prompt.get("budget", None)
        target_roi = parsed_prompt.get("target_roi", None)
        campaign_type = parsed_prompt.get("campaign_type", "ASC")
        
        logger.info(f"✅ Brand: {brand_name}")
        logger.info(f"✅ Industry: {industry}")
        logger.info(f"✅ Audience: {audience}")
        if budget:
            logger.info(f"✅ Budget: ${budget:,.0f}")
        if target_roi:
            logger.info(f"✅ Target ROI: {target_roi}x")
        
        # ====================================================================
        # PHASE 2: Industry Classification & LTV Prediction
        # ====================================================================
        logger.info("📊 PHASE 2: Predicting LTV baseline...")
        
        # Map industry to LTV baseline
        ltv_baseline = self._get_industry_ltv(industry, parsed_prompt.get("business_model"))
        logger.info(f"✅ LTV Baseline: ${ltv_baseline:.2f}")
        
        # Calculate max CPA from ROI target
        max_cpa = None
        if target_roi and target_roi > 0:
            max_cpa = ltv_baseline / target_roi
            logger.info(f"✅ Max CPA: ${max_cpa:.2f} (to achieve {target_roi}x ROI)")
        
        # ====================================================================
        # PHASE 3: Strategic Planning (SyncBrain)
        # ====================================================================
        logger.info("🧠 PHASE 3: Generating campaign strategy...")
        
        brand_context = {
            "brand_name": brand_name,
            "industry_profile": {
                "category": industry,
                "campaign_type": campaign_type,
                "ltv_baseline": ltv_baseline
            },
            "tone": parsed_prompt.get("tone", "professional"),
            "key_values": parsed_prompt.get("key_values", [])
        }
        
        try:
            campaign_strategy = await self.syncbrain.plan_campaign_strategy(brand_context)
        except Exception as e:
            logger.warning(f"SyncBrain strategy generation failed: {e}. Using fallback.")
            campaign_strategy = {
                "target_audience": audience,
                "key_message": parsed_prompt.get("key_message", f"Discover {brand_name}"),
                "tone": parsed_prompt.get("tone", "professional")
            }
        
        logger.info(f"✅ Target Audience: {campaign_strategy.get('target_audience')}")
        logger.info(f"✅ Key Message: {campaign_strategy.get('key_message')}")
        
        # ====================================================================
        # PHASE 4: Creative Generation (SyncCreate or User-Provided)
        # ====================================================================
        logger.info("🎨 PHASE 4: Processing ad creatives...")
        
        # Check for user-provided assets (BYOC - Bring Your Own Creative)
        user_ad_copies = user_assets.get("ad_copies", []) if user_assets else []
        user_images = user_assets.get("images", []) if user_assets else []
        user_videos = user_assets.get("videos", []) if user_assets else []
        user_descriptions = user_assets.get("descriptions", []) if user_assets else []
        
        has_user_content = any([user_ad_copies, user_images, user_videos, user_descriptions])
        
        if has_user_content:
            logger.info(f"📦 User provided: {len(user_ad_copies)} ad copies, {len(user_images)} images, {len(user_videos)} videos")
        
        try:
            # Generate ad copies (only if not provided by user)
            if user_ad_copies:
                ad_copies = []
                logger.info("⏭️  Skipping ad copy generation (user-provided)")
            else:
                ad_copies = await self.synccreate.generate_ad_copies(
                    brand_name=brand_name,
                    campaign_brief=campaign_strategy,
                    count=5
                )
                logger.info(f"✅ Generated {len(ad_copies)} ad copy variations")
            
            # Generate image prompts (only if not provided by user)
            if user_images:
                image_prompts = []
                logger.info("⏭️  Skipping image generation (user-provided)")
            else:
                image_prompts = await self.synccreate.generate_image_prompts(
                    brand_data=brand_context,
                    count=3
                )
                logger.info(f"✅ Generated {len(image_prompts)} image prompts")
            
            # Generate video prompts (only if not provided by user)
            if user_videos:
                video_prompts = []
                logger.info("⏭️  Skipping video generation (user-provided)")
            else:
                video_prompts = await self.synccreate.generate_video_prompts(
                    brand_data=brand_context,
                    count=2
                )
                logger.info(f"✅ Generated {len(video_prompts)} video prompts")
            
        except Exception as e:
            logger.warning(f"SyncCreate generation failed: {e}. Using placeholder assets.")
            ad_copies = [
                f"Discover {brand_name} - Transform your experience",
                f"{brand_name}: Quality you can trust",
                f"Join thousands who love {brand_name}",
                f"Experience the {brand_name} difference today",
                f"Limited time offer: Get started with {brand_name}"
            ]
            image_prompts = [
                f"Professional product shot of {brand_name} products, clean background, studio lighting",
                f"{brand_name} lifestyle image, happy customers, modern aesthetic",
                f"Abstract brand identity for {brand_name}, vibrant colors, minimalist design"
            ]
            video_prompts = [
                f"{brand_name} product showcase video, smooth camera movement, professional lighting",
                f"{brand_name} customer testimonial montage, authentic stories, cinematic quality"
            ]
        
        # ====================================================================
        # PHASE 5: Brand Safety & Compliance (SyncShield)
        # ====================================================================
        logger.info("🛡️ PHASE 5: Validating brand safety and compliance...")
        
        try:
            safety_check = await self.syncshield.validate_brand_safety(
                ad_copies=ad_copies,
                brand_name=brand_name
            )
            brand_safe = safety_check.get("all_safe", True)
            compliance_status = "approved" if brand_safe else "review_required"
            logger.info(f"✅ Brand Safety: {'PASS' if brand_safe else 'REVIEW REQUIRED'}")
        except Exception as e:
            logger.warning(f"SyncShield validation failed: {e}. Proceeding with caution.")
            brand_safe = False
            compliance_status = "validation_failed"
        
        # ====================================================================
        # Create Deployment Object
        # ====================================================================
        # Determine asset source
        if has_user_content and (ad_copies or image_prompts or video_prompts):
            assets_source = "hybrid"  # Mix of user-provided and generated
        elif has_user_content:
            assets_source = "user_provided"  # All user-provided
        else:
            assets_source = "generated"  # All AI-generated
        
        deployment = CampaignDeployment(
            deployment_id=deployment_id,
            url=None,  # No URL for prompt-based campaigns
            brand_name=brand_name,
            industry_category=industry,
            campaign_type=campaign_type,
            ltv_baseline=ltv_baseline,
            budget=budget,
            target_roi=target_roi,
            max_cpa=max_cpa,
            ad_copies=ad_copies,
            image_prompts=image_prompts,
            video_prompts=video_prompts,
            user_provided_ad_copies=user_ad_copies,
            user_provided_images=user_images,
            user_provided_videos=user_videos,
            user_provided_descriptions=user_descriptions,
            assets_source=assets_source,
            brand_safe=brand_safe,
            compliance_status=compliance_status,
            deployment_status="draft"
        )
        
        # ====================================================================
        # PHASE 6: Campaign Deployment (SyncFlow) - Optional
        # ====================================================================
        if auto_deploy and brand_safe:
            logger.info("🚀 PHASE 6: Deploying campaign to SyncFlow...")
            
            try:
                deployment_result = await self.syncflow.deploy_campaign(
                    campaign_data={
                        "brand_name": brand_name,
                        "ad_copies": ad_copies,
                        "image_prompts": image_prompts,
                        "campaign_type": campaign_type,
                        "target_audience": campaign_strategy.get("target_audience"),
                        "budget": budget,
                        "max_cpa": max_cpa
                    },
                    ltv_constraint=ltv_baseline
                )
                
                deployment.syncflow_deployment_id = deployment_result.get("deployment_id")
                deployment.deployment_status = "deployed"
                deployment.deployed_at = datetime.utcnow()
                
                logger.info(f"✅ Deployed to SyncFlow: {deployment.syncflow_deployment_id}")
                if budget:
                    logger.info(f"✅ Budget allocated: ${budget:,.0f}")
                if max_cpa:
                    logger.info(f"✅ Max CPA constraint: ${max_cpa:.2f}")
            except Exception as e:
                logger.error(f"SyncFlow deployment failed: {e}")
                deployment.deployment_status = "deployment_failed"
        elif auto_deploy and not brand_safe:
            logger.warning("⚠️ Auto-deploy skipped due to brand safety concerns")
            deployment.deployment_status = "safety_hold"
        
        # ====================================================================
        # PHASE 7: Audit Logging (SyncShield)
        # ====================================================================
        logger.info("📝 PHASE 7: Logging campaign deployment...")
        
        await self.syncshield.log_campaign_deployment(deployment.to_dict())
        
        # ====================================================================
        # Complete
        # ====================================================================
        logger.info(f"✅ Council of Nine: Campaign creation complete!")
        logger.info(f"📊 Status: {deployment.deployment_status}")
        logger.info(f"🎯 Assets: {len(ad_copies)} ad copies, {len(image_prompts)} image prompts, {len(video_prompts)} video prompts")
        
        return deployment
    
    def _fallback_parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """Fallback prompt parser using simple keyword extraction"""
        import re
        
        prompt_lower = prompt.lower()
        parsed = {}
        
        # Extract budget
        budget_match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d+)?)[km]?\s*(?:budget)?', prompt_lower)
        if budget_match:
            budget_str = budget_match.group(1).replace(',', '')
            budget = float(budget_str)
            if 'k' in prompt_lower[budget_match.start():budget_match.end()+2]:
                budget *= 1000
            elif 'm' in prompt_lower[budget_match.start():budget_match.end()+2]:
                budget *= 1000000
            parsed["budget"] = budget
        
        # Extract ROI
        roi_match = re.search(r'roi\s*(\d+(?:\.\d+)?)x?', prompt_lower)
        if roi_match:
            parsed["target_roi"] = float(roi_match.group(1))
        
        # Detect industry keywords
        industry_map = {
            "saas": "SaaS & Software",
            "software": "SaaS & Software",
            "ecommerce": "E-commerce & Retail",
            "e-commerce": "E-commerce & Retail",
            "shop": "E-commerce & Retail",
            "retail": "E-commerce & Retail",
            "game": "Mobile Gaming",
            "gaming": "Mobile Gaming",
            "mobile game": "Mobile Gaming",
            "education": "Education & E-Learning",
            "learning": "Education & E-Learning",
            "health": "Health & Wellness",
            "wellness": "Health & Wellness",
            "fitness": "Health & Wellness",
            "finance": "Financial Services",
            "financial": "Financial Services",
            "service": "Professional Services",
            "b2b": "Professional Services"
        }
        
        detected_industry = "General"
        for keyword, industry in industry_map.items():
            if keyword in prompt_lower:
                detected_industry = industry
                break
        
        parsed["industry"] = detected_industry
        parsed["brand_name"] = "New Product Launch"
        parsed["target_audience"] = "Broad audience"
        parsed["campaign_type"] = "ASC"
        
        # Detect audience keywords
        if "b2b" in prompt_lower or "enterprise" in prompt_lower:
            parsed["target_audience"] = "B2B enterprise decision makers"
            parsed["campaign_type"] = "ALC"
        elif "b2c" in prompt_lower or "consumer" in prompt_lower:
            parsed["target_audience"] = "B2C consumers"
        
        return parsed
    
    def _get_industry_ltv(self, industry: str, business_model: Optional[str] = None) -> float:
        """Get LTV baseline for industry"""
        ltv_map = {
            "E-commerce & Retail": 120.0,
            "SaaS & Software": 800.0,
            "Mobile Gaming": 50.0,
            "Professional Services": 1500.0,
            "Education & E-Learning": 300.0,
            "Health & Wellness": 200.0,
            "Financial Services": 800.0,
            "General": 100.0
        }
        
        # Adjust for business model
        base_ltv = ltv_map.get(industry, 100.0)
        
        if business_model == "B2B" or business_model == "enterprise":
            base_ltv *= 2.5  # B2B typically has higher LTV
        elif business_model == "freemium":
            base_ltv *= 0.6  # Freemium has lower conversion LTV
        
        return base_ltv


# ============================================================================
# Convenience Functions
# ============================================================================

async def create_campaign_from_url(
    url: str,
    auto_deploy: bool = False,
    **service_urls
) -> CampaignDeployment:
    """
    Convenience function to create a campaign from a URL.
    
    Usage:
        deployment = await create_campaign_from_url("https://example.com")
    """
    council = CouncilOfNine(**service_urls)
    return await council.url_to_campaign(url, auto_deploy=auto_deploy)


async def create_campaign_from_prompt(
    prompt: str,
    auto_deploy: bool = False,
    **service_urls
) -> CampaignDeployment:
    """
    Convenience function to create a campaign from a natural language prompt.
    
    Usage:
        deployment = await create_campaign_from_prompt(
            "Launch product with $100k budget, target ROI 3x"
        )
    """
    council = CouncilOfNine(**service_urls)
    return await council.prompt_to_campaign(prompt, auto_deploy=auto_deploy)
