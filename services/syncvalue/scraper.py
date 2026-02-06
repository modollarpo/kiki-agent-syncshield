"""
SyncScrape Module - Brand Identity Extraction and Campaign Asset Generation

This module extracts brand identity from URLs using Playwright/BeautifulSoup,
sends data to SyncBrain for CampaignBrief generation, triggers SyncCreate for
asset generation, and validates through SyncShield for brand safety.

Architecture: Clean Architecture + DDD
Dependencies: Playwright, BeautifulSoup, httpx
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import re

# Web scraping
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup
import httpx

# Configuration
from shared.config import ServiceConfig

# Setup logging
logger = logging.getLogger("syncscrape")
logging.basicConfig(level=logging.INFO)


# ============================================================================
# Domain Models
# ============================================================================

@dataclass
class IndustryProfile:
    """Industry classification and targeting strategy"""
    category: str  # e.g., "E-commerce", "SaaS", "Mobile Gaming"
    subcategory: Optional[str] = None  # e.g., "Fast Fashion", "Enterprise B2B"
    business_model: str = "B2C"  # B2C, B2B, B2B2C
    price_point: str = "mid"  # low, mid, high, premium
    campaign_type: str = "ASC"  # ASC (Advantage+ Sales) or ALC (Advantage+ Leads)
    ltv_baseline: float = 0.0  # Estimated baseline LTV for industry
    retention_score: float = 0.5  # 0-1 score for expected retention
    confidence: float = 0.0  # 0-1 confidence in classification


@dataclass
class BrandIdentity:
    """Domain model for extracted brand identity"""
    url: str
    brand_name: Optional[str] = None
    primary_colors: List[str] = field(default_factory=list)
    secondary_colors: List[str] = field(default_factory=list)
    tone: Optional[str] = None  # e.g., "professional", "casual", "playful"
    product_catalog: List[Dict[str, Any]] = field(default_factory=list)
    meta_description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    logo_url: Optional[str] = None
    industry_profile: Optional[IndustryProfile] = None
    extracted_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API consumption"""
        result = {
            "url": self.url,
            "brand_name": self.brand_name,
            "primary_colors": self.primary_colors,
            "secondary_colors": self.secondary_colors,
            "tone": self.tone,
            "product_catalog": self.product_catalog,
            "meta_description": self.meta_description,
            "keywords": self.keywords,
            "logo_url": self.logo_url,
            "extracted_at": self.extracted_at.isoformat()
        }
        if self.industry_profile:
            result["industry_profile"] = {
                "category": self.industry_profile.category,
                "subcategory": self.industry_profile.subcategory,
                "business_model": self.industry_profile.business_model,
                "price_point": self.industry_profile.price_point,
                "campaign_type": self.industry_profile.campaign_type,
                "ltv_baseline": self.industry_profile.ltv_baseline,
                "retention_score": self.industry_profile.retention_score,
                "confidence": self.industry_profile.confidence
            }
        return result


@dataclass
class CampaignBrief:
    """Domain model for campaign brief from SyncBrain"""
    campaign_id: str
    brand_identity: BrandIdentity
    target_audience: str
    key_message: str
    tone_guidance: str
    visual_guidelines: Dict[str, Any]
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GeneratedAsset:
    """Domain model for generated creative asset"""
    asset_id: str
    asset_type: str  # "copy" or "image_prompt"
    content: str
    brand_safe: bool = False
    sentiment_score: Optional[float] = None
    compliance_status: Optional[str] = None


# ============================================================================
# Data Extraction Layer
# ============================================================================

class BrandIdentityExtractor:
    """Extracts brand identity from websites using Playwright + BeautifulSoup"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.browser:
            await self.browser.close()
    
    async def extract(self, url: str) -> BrandIdentity:
        """
        Extract brand identity from a URL.
        
        Args:
            url: Target website URL
            
        Returns:
            BrandIdentity object with extracted data
        """
        logger.info(f"Extracting brand identity from: {url}")
        
        if not self.browser:
            raise RuntimeError("Extractor not initialized. Use async with context manager.")
        
        # Create new page
        page: Page = await self.browser.new_page()
        
        try:
            # Navigate to URL
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)  # Wait for dynamic content
            
            # Get page content
            html_content = await page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract brand identity components
            brand_identity = BrandIdentity(url=url)
            
            # 1. Extract brand name
            brand_identity.brand_name = self._extract_brand_name(soup, page)
            
            # 2. Extract colors from CSS
            brand_identity.primary_colors, brand_identity.secondary_colors = \
                await self._extract_colors(page)
            
            # 3. Infer tone from content
            brand_identity.tone = self._infer_tone(soup)
            
            # 4. Extract product catalog
            brand_identity.product_catalog = self._extract_products(soup)
            
            # 5. Extract meta information
            brand_identity.meta_description = self._extract_meta_description(soup)
            brand_identity.keywords = self._extract_keywords(soup)
            
            # 6. Extract logo URL
            brand_identity.logo_url = self._extract_logo(soup, url)
            
            # 7. Classify industry and determine campaign strategy
            brand_identity.industry_profile = self._classify_industry(brand_identity, soup)
            
            logger.info(f"Successfully extracted brand identity for: {brand_identity.brand_name}")
            logger.info(f"Industry: {brand_identity.industry_profile.category if brand_identity.industry_profile else 'Unknown'}")
            return brand_identity
            
        except Exception as e:
            logger.error(f"Error extracting brand identity from {url}: {e}")
            raise
        finally:
            await page.close()
    
    def _extract_brand_name(self, soup: BeautifulSoup, page: Page) -> Optional[str]:
        """Extract brand/company name from various sources"""
        # Try og:site_name
        og_site = soup.find("meta", property="og:site_name")
        if og_site and og_site.get("content"):
            return og_site["content"]
        
        # Try title tag
        title = soup.find("title")
        if title:
            return title.text.split("|")[0].split("-")[0].strip()
        
        # Try h1
        h1 = soup.find("h1")
        if h1:
            return h1.text.strip()
        
        return None
    
    async def _extract_colors(self, page: Page) -> tuple[List[str], List[str]]:
        """Extract color palette from page CSS"""
        try:
            # Extract computed styles for common elements
            colors = await page.evaluate("""
                () => {
                    const extractedColors = new Set();
                    const elements = document.querySelectorAll('header, nav, .hero, .banner, button, a, .cta');
                    elements.forEach(el => {
                        const styles = window.getComputedStyle(el);
                        if (styles.backgroundColor && styles.backgroundColor !== 'rgba(0, 0, 0, 0)') {
                            extractedColors.add(styles.backgroundColor);
                        }
                        if (styles.color) {
                            extractedColors.add(styles.color);
                        }
                    });
                    return Array.from(extractedColors);
                }
            """)
            
            # Parse and convert to hex
            hex_colors = []
            for color in colors[:10]:  # Limit to 10 colors
                hex_color = self._rgb_to_hex(color)
                if hex_color:
                    hex_colors.append(hex_color)
            
            # Split into primary (first 3) and secondary
            primary = hex_colors[:3]
            secondary = hex_colors[3:6]
            
            return primary, secondary
            
        except Exception as e:
            logger.warning(f"Error extracting colors: {e}")
            return [], []
    
    def _rgb_to_hex(self, rgb_string: str) -> Optional[str]:
        """Convert RGB/RGBA string to hex color"""
        try:
            # Extract numbers from rgb(a) string
            match = re.search(r'(\d+),\s*(\d+),\s*(\d+)', rgb_string)
            if match:
                r, g, b = match.groups()
                return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
        except Exception:
            pass
        return None
    
    def _infer_tone(self, soup: BeautifulSoup) -> str:
        """Infer brand tone from content analysis"""
        # Get all text content
        text_content = soup.get_text().lower()
        
        # Simple heuristic-based tone detection
        professional_keywords = ["enterprise", "solution", "professional", "business", "corporate"]
        casual_keywords = ["hey", "awesome", "cool", "easy", "simple"]
        playful_keywords = ["fun", "enjoy", "love", "exciting", "amazing"]
        luxury_keywords = ["premium", "exclusive", "luxury", "elegant", "sophisticated"]
        
        scores = {
            "professional": sum(1 for kw in professional_keywords if kw in text_content),
            "casual": sum(1 for kw in casual_keywords if kw in text_content),
            "playful": sum(1 for kw in playful_keywords if kw in text_content),
            "luxury": sum(1 for kw in luxury_keywords if kw in text_content),
        }
        
        # Return tone with highest score, default to professional
        tone = max(scores.items(), key=lambda x: x[1])[0]
        return tone if scores[tone] > 0 else "professional"
    
    def _extract_products(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract product information from common e-commerce patterns"""
        products = []
        
        # Look for common product selectors
        product_selectors = [
            ".product-item", ".product-card", "[data-product]",
            ".item", "article.product", ".product"
        ]
        
        for selector in product_selectors:
            items = soup.select(selector)[:10]  # Limit to 10 products
            for item in items:
                product = {}
                
                # Extract name
                name_tag = item.find(["h2", "h3", "h4", ".product-name", ".title"])
                if name_tag:
                    product["name"] = name_tag.text.strip()
                
                # Extract price
                price_tag = item.find(class_=re.compile(r"price"))
                if price_tag:
                    product["price"] = price_tag.text.strip()
                
                # Extract image
                img_tag = item.find("img")
                if img_tag and img_tag.get("src"):
                    product["image_url"] = img_tag["src"]
                
                if product.get("name"):
                    products.append(product)
            
            if products:
                break  # Found products, stop searching
        
        return products
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract meta description"""
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            return meta["content"]
        
        # Try og:description
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return og_desc["content"]
        
        return None
    
    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract keywords from meta tags and headings"""
        keywords = []
        
        # From meta keywords
        meta_kw = soup.find("meta", attrs={"name": "keywords"})
        if meta_kw and meta_kw.get("content"):
            keywords.extend([kw.strip() for kw in meta_kw["content"].split(",")])
        
        # From headings
        for heading in soup.find_all(["h1", "h2", "h3"])[:10]:
            text = heading.text.strip()
            if text and len(text.split()) <= 5:  # Short headings only
                keywords.append(text)
        
        return keywords[:15]  # Limit to 15 keywords
    
    def _extract_logo(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract logo URL"""
        # Try common logo selectors
        logo_selectors = [
            "img.logo", ".logo img", "[class*='logo'] img",
            "header img", ".brand img"
        ]
        
        for selector in logo_selectors:
            logo = soup.select_one(selector)
            if logo and logo.get("src"):
                src = logo["src"]
                # Make absolute URL if relative
                if src.startswith("//"):
                    return f"https:{src}"
                elif src.startswith("/"):
                    from urllib.parse import urljoin
                    return urljoin(base_url, src)
                elif src.startswith("http"):
                    return src
        
        return None
    
    def _classify_industry(self, brand_identity: BrandIdentity, soup: BeautifulSoup) -> IndustryProfile:
        \"\"\"
        Classify industry and determine optimal campaign strategy.
        
        Uses heuristic-based classification from:
        - Product catalog (presence/pricing)
        - Keywords and content
        - Meta description
        - URL patterns
        \"\"\"
        logger.info("Classifying industry profile...")
        
        # Get all text content for analysis
        text_content = soup.get_text().lower()
        keywords_lower = [kw.lower() for kw in brand_identity.keywords]
        meta_lower = (brand_identity.meta_description or "").lower()
        url_lower = brand_identity.url.lower()
        
        # Initialize default profile
        profile = IndustryProfile(
            category="General",
            business_model="B2C",
            price_point="mid",
            campaign_type="ASC",
            ltv_baseline=50.0,
            retention_score=0.5,
            confidence=0.3
        )
        
        # Industry classification rules
        confidence_boost = 0.0
        
        # E-commerce & Retail Detection
        ecommerce_signals = [
            "shop", "store", "cart", "checkout", "product", "buy", 
            "price", "shipping", "returns", "sale"
        ]
        ecommerce_score = sum(1 for signal in ecommerce_signals if signal in text_content)
        has_products = len(brand_identity.product_catalog) > 0
        
        if ecommerce_score >= 3 or has_products:
            profile.category = "E-commerce & Retail"
            profile.campaign_type = "ASC"  # Advantage+ Shopping Campaigns
            profile.ltv_baseline = 75.0
            profile.retention_score = 0.6
            confidence_boost = 0.3
            
            # Subcategory detection
            if any(x in text_content for x in ["fashion", "clothing", "apparel", "shoes"]):
                profile.subcategory = "Fast Fashion"
                profile.price_point = "mid"
                profile.ltv_baseline = 60.0
            elif any(x in text_content for x in ["luxury", "premium", "designer"]):
                profile.subcategory = "Luxury Goods"
                profile.price_point = "premium"
                profile.ltv_baseline = 250.0
                profile.retention_score = 0.75
            elif any(x in text_content for x in ["electronics", "tech", "gadget"]):
                profile.subcategory = "Consumer Electronics"
                profile.price_point = "high"
                profile.ltv_baseline = 150.0
            
            # Price point detection from product catalog
            if has_products:
                prices = [p.get("price", 0) for p in brand_identity.product_catalog if "price" in p]
                if prices:
                    avg_price = sum(prices) / len(prices)
                    if avg_price < 30:
                        profile.price_point = "low"
                    elif avg_price < 100:
                        profile.price_point = "mid"
                    elif avg_price < 500:
                        profile.price_point = "high"
                    else:
                        profile.price_point = "premium"
                        profile.ltv_baseline = 200.0
        
        # SaaS & Software Detection
        saas_signals = [
            "saas", "software", "platform", "dashboard", "api", 
            "subscription", "enterprise", "solution", "cloud", "trial"
        ]
        saas_score = sum(1 for signal in saas_signals if signal in text_content)
        
        if saas_score >= 4:
            profile.category = "SaaS & Software"
            profile.business_model = "B2B" if "enterprise" in text_content or "business" in text_content else "B2C"
            profile.campaign_type = "ALC"  # Advantage+ Lead Campaigns for B2B
            profile.ltv_baseline = 500.0  # Higher LTV for software
            profile.retention_score = 0.85  # Software has high retention
            confidence_boost = 0.35
            
            if profile.business_model == "B2B":
                profile.subcategory = "Enterprise B2B"
                profile.price_point = "premium"
                profile.ltv_baseline = 2500.0
                profile.retention_score = 0.9
            else:
                profile.subcategory = "Consumer SaaS"
                profile.price_point = "mid"
                profile.ltv_baseline = 150.0
        
        # Mobile Gaming & Apps Detection
        gaming_signals = ["game", "play", "player", "download", "app", "mobile", "ios", "android"]
        gaming_score = sum(1 for signal in gaming_signals if signal in text_content)
        
        if gaming_score >= 3 or "game" in url_lower or "app" in url_lower:
            profile.category = "Mobile Gaming & Apps"
            profile.campaign_type = "ASC"  # App install campaigns
            profile.ltv_baseline = 25.0  # Lower initial LTV but high volume
            profile.retention_score = 0.4  # Gaming has lower retention
            confidence_boost = 0.3
            
            if "casino" in text_content or "slots" in text_content:
                profile.subcategory = "Casino & Gambling"
                profile.ltv_baseline = 100.0  # Whales drive high LTV
                profile.retention_score = 0.7
            elif "puzzle" in text_content or "casual" in text_content:
                profile.subcategory = "Casual Gaming"
                profile.price_point = "low"
        
        # Service & Professional Services Detection
        service_signals = ["service", "consult", "agency", "professional", "expert", "hire", "book"]
        service_score = sum(1 for signal in service_signals if signal in text_content)
        
        if service_score >= 3 and ecommerce_score < 2:
            profile.category = "Professional Services"
            profile.business_model = "B2B"
            profile.campaign_type = "ALC"  # Lead generation
            profile.ltv_baseline = 1500.0  # High-ticket services
            profile.retention_score = 0.7
            profile.price_point = "high"
            confidence_boost = 0.25
        
        # Education & Learning Detection
        education_signals = ["course", "learn", "training", "education", "tutor", "study", "certification"]
        education_score = sum(1 for signal in education_signals if signal in text_content)
        
        if education_score >= 3:
            profile.category = "Education & E-Learning"
            profile.campaign_type = "ALC"  # Lead gen for course signups
            profile.ltv_baseline = 300.0
            profile.retention_score = 0.65
            confidence_boost = 0.3
        
        # Health & Wellness Detection
        health_signals = ["health", "wellness", "fitness", "nutrition", "medical", "therapy"]
        health_score = sum(1 for signal in health_signals if signal in text_content)
        
        if health_score >= 2:
            profile.category = "Health & Wellness"
            profile.campaign_type = "ASC"  # E-commerce or lead gen
            profile.ltv_baseline = 200.0
            profile.retention_score = 0.75
            confidence_boost = 0.25
        
        # Financial Services Detection
        financial_signals = ["finance", "investment", "crypto", "trading", "bank", "insurance"]
        financial_score = sum(1 for signal in financial_signals if signal in text_content)
        
        if financial_score >= 2:
            profile.category = "Financial Services"
            profile.business_model = "B2B2C"
            profile.campaign_type = "ALC"  # High compliance, lead-focused
            profile.ltv_baseline = 800.0
            profile.retention_score = 0.8
            profile.price_point = "premium"
            confidence_boost = 0.3
        
        # Calculate final confidence score
        profile.confidence = min(0.95, 0.5 + confidence_boost)
        
        logger.info(
            f"Classified as: {profile.category} ({profile.subcategory or 'General'}) "
            f"- {profile.campaign_type} - LTV: ${profile.ltv_baseline:.2f} "
            f"- Confidence: {profile.confidence:.2f}"
        )
        
        return profile


# ============================================================================
# Service Integration Layer
# ============================================================================

class SyncBrainClient:
    """Client for SyncBrain LLM orchestration service"""
    
    def __init__(self, base_url: str = "http://syncbrain:8001"):
        self.base_url = base_url
        self.timeout = 30.0
    
    async def generate_campaign_brief(
        self, 
        brand_identity: BrandIdentity,
        campaign_goal: str = "brand awareness"
    ) -> CampaignBrief:
        """
        Generate a CampaignBrief using SyncBrain's LLM capabilities.
        
        Args:
            brand_identity: Extracted brand identity data
            campaign_goal: Campaign objective
            
        Returns:
            CampaignBrief with strategy and guidelines
        """
        logger.info(f"Requesting campaign brief from SyncBrain for: {brand_identity.brand_name}")
        
        # Prepare context for SyncBrain
        context = {
            "brand_name": brand_identity.brand_name,
            "brand_colors": brand_identity.primary_colors,
            "brand_tone": brand_identity.tone,
            "products": brand_identity.product_catalog,
            "description": brand_identity.meta_description,
            "keywords": brand_identity.keywords,
            "campaign_goal": campaign_goal
        }
        
        payload = {
            "user_id": f"scraper_{brand_identity.brand_name}",
            "context": context
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/plan-strategy",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                
                # Parse LLM response into campaign brief
                campaign_id = f"campaign_{datetime.utcnow().timestamp()}"
                
                campaign_brief = CampaignBrief(
                    campaign_id=campaign_id,
                    brand_identity=brand_identity,
                    target_audience=result.get("plan", "").split(".")[0],  # First sentence
                    key_message=result.get("plan", ""),
                    tone_guidance=brand_identity.tone or "professional",
                    visual_guidelines={
                        "colors": brand_identity.primary_colors,
                        "logo": brand_identity.logo_url,
                        "style": brand_identity.tone
                    }
                )
                
                logger.info(f"Generated campaign brief: {campaign_id}")
                return campaign_brief
                
            except httpx.HTTPError as e:
                logger.error(f"SyncBrain API error: {e}")
                raise RuntimeError(f"Failed to generate campaign brief: {e}")


class SyncCreateClient:
    """Client for SyncCreate creative generation service"""
    
    def __init__(self, base_url: str = "http://synccreate:8004"):
        self.base_url = base_url
        self.timeout = 60.0
    
    async def generate_ad_variations(
        self,
        campaign_brief: CampaignBrief,
        num_copies: int = 5,
        num_image_prompts: int = 3
    ) -> Dict[str, List[GeneratedAsset]]:
        """
        Generate ad copy variations and image prompts based on campaign brief.
        
        Args:
            campaign_brief: Campaign brief from SyncBrain
            num_copies: Number of ad copy variations to generate
            num_image_prompts: Number of image prompts to generate
            
        Returns:
            Dictionary with 'copies' and 'image_prompts' lists
        """
        logger.info(f"Generating {num_copies} ad copies and {num_image_prompts} image prompts")
        
        assets = {
            "copies": [],
            "image_prompts": []
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Generate ad copy variations
            for i in range(num_copies):
                copy_prompt = (
                    f"Write a {campaign_brief.tone_guidance} ad copy for {campaign_brief.brand_identity.brand_name}. "
                    f"Target audience: {campaign_brief.target_audience}. "
                    f"Key message: {campaign_brief.key_message}. "
                    f"Variation {i+1} of {num_copies}. Keep it under 100 words."
                )
                
                try:
                    response = await client.post(
                        f"{self.base_url}/generate",
                        json={
                            "creative_type": "text",
                            "prompt": copy_prompt,
                            "user_id": f"scraper_{campaign_brief.campaign_id}",
                            "variant": "openai"
                        },
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        asset = GeneratedAsset(
                            asset_id=result.get("creative_id", f"copy_{i}"),
                            asset_type="copy",
                            content=result.get("creative_url", copy_prompt)  # Fallback to prompt
                        )
                        assets["copies"].append(asset)
                        logger.info(f"Generated ad copy variation {i+1}")
                    else:
                        logger.warning(f"Failed to generate copy {i+1}: {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Error generating copy {i+1}: {e}")
            
            # Generate image prompts
            for i in range(num_image_prompts):
                image_prompt = (
                    f"A {campaign_brief.tone_guidance} image for {campaign_brief.brand_identity.brand_name}. "
                    f"Colors: {', '.join(campaign_brief.visual_guidelines.get('colors', []))}. "
                    f"Style: {campaign_brief.visual_guidelines.get('style', 'professional')}. "
                    f"Variation {i+1}."
                )
                
                asset = GeneratedAsset(
                    asset_id=f"img_prompt_{i}",
                    asset_type="image_prompt",
                    content=image_prompt
                )
                assets["image_prompts"].append(asset)
                logger.info(f"Generated image prompt {i+1}")
        
        logger.info(f"Generated {len(assets['copies'])} copies and {len(assets['image_prompts'])} image prompts")
        return assets


class SyncShieldClient:
    """Client for SyncShield compliance and brand safety service"""
    
    def __init__(self, base_url: str = "http://syncshield:8006"):
        self.base_url = base_url
        self.timeout = 10.0
    
    async def validate_asset(
        self,
        asset: GeneratedAsset,
        brand_identity: BrandIdentity
    ) -> GeneratedAsset:
        """
        Validate asset for brand safety and sentiment alignment.
        
        Args:
            asset: Generated asset to validate
            brand_identity: Original brand identity for alignment check
            
        Returns:
            Updated asset with compliance status
        """
        logger.info(f"Validating asset {asset.asset_id} through SyncShield")
        
        # For now, use a simple heuristic-based validation since SyncShield
        # is implemented in Go. In production, this would call the actual
        # compliance API or use gRPC.
        
        # Simple sentiment analysis (placeholder - would use real NLP)
        content_lower = asset.content.lower()
        
        # Check for negative keywords
        negative_keywords = ["hate", "violent", "offensive", "inappropriate", "scam"]
        has_negative = any(keyword in content_lower for keyword in negative_keywords)
        
        # Check for brand alignment
        brand_keywords = brand_identity.keywords[:5] if brand_identity.keywords else []
        has_brand_alignment = any(
            keyword.lower() in content_lower 
            for keyword in brand_keywords
        ) if brand_keywords else True
        
        # Calculate sentiment score (0-1, higher is better)
        positive_keywords = ["great", "amazing", "best", "excellent", "premium", "quality"]
        positive_count = sum(1 for kw in positive_keywords if kw in content_lower)
        sentiment_score = min(1.0, 0.5 + (positive_count * 0.1))
        
        # Determine if brand safe
        brand_safe = (
            not has_negative and 
            has_brand_alignment and 
            sentiment_score >= 0.5
        )
        
        # Update asset
        asset.brand_safe = brand_safe
        asset.sentiment_score = sentiment_score
        asset.compliance_status = "approved" if brand_safe else "rejected"
        
        logger.info(
            f"Asset {asset.asset_id} validation: "
            f"brand_safe={brand_safe}, sentiment={sentiment_score:.2f}"
        )
        
        return asset


# ============================================================================
# Orchestration Layer
# ============================================================================

class SyncScrapeOrchestrator:
    """
    Main orchestrator for the SyncScrape workflow.
    Coordinates extraction, enrichment, generation, and validation.
    """
    
    def __init__(
        self,
        syncbrain_url: str = "http://syncbrain:8001",
        synccreate_url: str = "http://synccreate:8004",
        syncshield_url: str = "http://syncshield:8006"
    ):
        self.syncbrain_client = SyncBrainClient(syncbrain_url)
        self.synccreate_client = SyncCreateClient(synccreate_url)
        self.syncshield_client = SyncShieldClient(syncshield_url)
    
    async def execute(
        self,
        url: str,
        campaign_goal: str = "brand awareness",
        num_ad_copies: int = 5,
        num_image_prompts: int = 3
    ) -> Dict[str, Any]:
        """
        Execute the complete SyncScrape workflow.
        
        Args:
            url: Target website URL to scrape
            campaign_goal: Campaign objective
            num_ad_copies: Number of ad copy variations to generate
            num_image_prompts: Number of image prompts to generate
            
        Returns:
            Complete result including brand identity, campaign brief, and validated assets
        """
        logger.info(f"Starting SyncScrape workflow for: {url}")
        
        # Step 1: Data Extraction
        async with BrandIdentityExtractor() as extractor:
            brand_identity = await extractor.extract(url)
        
        logger.info(f"✓ Extracted brand identity: {brand_identity.brand_name}")
        
        # Step 2: Context Enrichment
        campaign_brief = await self.syncbrain_client.generate_campaign_brief(
            brand_identity, 
            campaign_goal
        )
        
        logger.info(f"✓ Generated campaign brief: {campaign_brief.campaign_id}")
        
        # Step 3: Asset Generation
        generated_assets = await self.synccreate_client.generate_ad_variations(
            campaign_brief,
            num_ad_copies,
            num_image_prompts
        )
        
        logger.info(
            f"✓ Generated {len(generated_assets['copies'])} ad copies and "
            f"{len(generated_assets['image_prompts'])} image prompts"
        )
        
        # Step 4: Safety Check
        validated_assets = {
            "copies": [],
            "image_prompts": []
        }
        
        # Validate all copies
        for asset in generated_assets["copies"]:
            validated = await self.syncshield_client.validate_asset(asset, brand_identity)
            validated_assets["copies"].append(validated)
        
        # Validate all image prompts
        for asset in generated_assets["image_prompts"]:
            validated = await self.syncshield_client.validate_asset(asset, brand_identity)
            validated_assets["image_prompts"].append(validated)
        
        # Calculate approval rates
        total_assets = len(validated_assets["copies"]) + len(validated_assets["image_prompts"])
        approved_assets = sum(
            1 for assets in validated_assets.values() 
            for asset in assets 
            if asset.brand_safe
        )
        approval_rate = (approved_assets / total_assets * 100) if total_assets > 0 else 0
        
        logger.info(f"✓ Validated all assets: {approval_rate:.1f}% approval rate")
        
        # Compile results
        result = {
            "status": "success",
            "brand_identity": brand_identity.to_dict(),
            "campaign_brief": {
                "campaign_id": campaign_brief.campaign_id,
                "target_audience": campaign_brief.target_audience,
                "key_message": campaign_brief.key_message,
                "tone_guidance": campaign_brief.tone_guidance,
                "visual_guidelines": campaign_brief.visual_guidelines
            },
            "generated_assets": {
                "copies": [
                    {
                        "asset_id": a.asset_id,
                        "content": a.content,
                        "brand_safe": a.brand_safe,
                        "sentiment_score": a.sentiment_score,
                        "compliance_status": a.compliance_status
                    }
                    for a in validated_assets["copies"]
                ],
                "image_prompts": [
                    {
                        "asset_id": a.asset_id,
                        "content": a.content,
                        "brand_safe": a.brand_safe,
                        "sentiment_score": a.sentiment_score,
                        "compliance_status": a.compliance_status
                    }
                    for a in validated_assets["image_prompts"]
                ]
            },
            "metrics": {
                "total_assets": total_assets,
                "approved_assets": approved_assets,
                "approval_rate": approval_rate,
                "extracted_products": len(brand_identity.product_catalog),
                "extracted_colors": len(brand_identity.primary_colors) + len(brand_identity.secondary_colors)
            }
        }
        
        logger.info(f"✓ SyncScrape workflow completed successfully for {brand_identity.brand_name}")
        return result


# ============================================================================
# CLI Interface
# ============================================================================

async def main():
    """CLI entry point for testing SyncScrape"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <url>")
        print("Example: python scraper.py https://example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    
    print(f"\n{'='*80}")
    print(f"SyncScrape - Brand Identity Extraction & Campaign Generation")
    print(f"{'='*80}\n")
    
    orchestrator = SyncScrapeOrchestrator()
    
    try:
        result = await orchestrator.execute(url)
        
        print(f"\n{'='*80}")
        print(f"RESULTS")
        print(f"{'='*80}\n")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        logger.error(f"Error executing SyncScrape: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
