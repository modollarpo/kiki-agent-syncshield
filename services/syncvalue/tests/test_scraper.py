"""
Tests for SyncScrape Module

Tests the brand identity extraction, service integrations, and complete workflow.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Import module under test
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from scraper import (
    BrandIdentity,
    CampaignBrief,
    GeneratedAsset,
    BrandIdentityExtractor,
    SyncBrainClient,
    SyncCreateClient,
    SyncShieldClient,
    SyncScrapeOrchestrator
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_brand_identity():
    """Sample brand identity for testing"""
    return BrandIdentity(
        url="https://example.com",
        brand_name="Example Corp",
        primary_colors=["#FF5733", "#33FF57"],
        secondary_colors=["#3357FF"],
        tone="professional",
        product_catalog=[
            {"name": "Product A", "price": "$99.99"},
            {"name": "Product B", "price": "$149.99"}
        ],
        meta_description="Example Corp - Leading solutions provider",
        keywords=["innovation", "quality", "service"],
        logo_url="https://example.com/logo.png"
    )


@pytest.fixture
def sample_campaign_brief(sample_brand_identity):
    """Sample campaign brief for testing"""
    return CampaignBrief(
        campaign_id="campaign_123",
        brand_identity=sample_brand_identity,
        target_audience="Tech professionals",
        key_message="Innovative solutions for modern businesses",
        tone_guidance="professional",
        visual_guidelines={
            "colors": ["#FF5733", "#33FF57"],
            "logo": "https://example.com/logo.png",
            "style": "professional"
        }
    )


@pytest.fixture
def sample_html():
    """Sample HTML for testing extraction"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Example Corp - Innovation Experts</title>
        <meta name="description" content="Example Corp provides innovative solutions">
        <meta name="keywords" content="innovation, technology, solutions">
        <meta property="og:site_name" content="Example Corp">
    </head>
    <body>
        <header>
            <img class="logo" src="/logo.png" alt="Example Corp">
        </header>
        <h1>Welcome to Example Corp</h1>
        <div class="product-item">
            <h3 class="product-name">Product A</h3>
            <span class="price">$99.99</span>
            <img src="/product-a.jpg">
        </div>
        <div class="product-item">
            <h3 class="product-name">Product B</h3>
            <span class="price">$149.99</span>
            <img src="/product-b.jpg">
        </div>
    </body>
    </html>
    """


# ============================================================================
# Unit Tests - Domain Models
# ============================================================================

def test_brand_identity_to_dict(sample_brand_identity):
    """Test BrandIdentity conversion to dictionary"""
    result = sample_brand_identity.to_dict()
    
    assert result["url"] == "https://example.com"
    assert result["brand_name"] == "Example Corp"
    assert result["primary_colors"] == ["#FF5733", "#33FF57"]
    assert result["tone"] == "professional"
    assert len(result["product_catalog"]) == 2
    assert "extracted_at" in result


# ============================================================================
# Unit Tests - BrandIdentityExtractor
# ============================================================================

@pytest.mark.asyncio
async def test_extract_brand_name_from_og_tag(sample_html):
    """Test brand name extraction from og:site_name"""
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(sample_html, 'html.parser')
    extractor = BrandIdentityExtractor()
    
    brand_name = extractor._extract_brand_name(soup, None)
    assert brand_name == "Example Corp"


@pytest.mark.asyncio
async def test_extract_products(sample_html):
    """Test product extraction"""
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(sample_html, 'html.parser')
    extractor = BrandIdentityExtractor()
    
    products = extractor._extract_products(soup)
    
    assert len(products) == 2
    assert products[0]["name"] == "Product A"
    assert products[0]["price"] == "$99.99"
    assert products[1]["name"] == "Product B"


@pytest.mark.asyncio
async def test_infer_tone():
    """Test tone inference"""
    from bs4 import BeautifulSoup
    
    extractor = BrandIdentityExtractor()
    
    # Professional tone
    html_professional = "<html><body>Enterprise business solution professional corporate</body></html>"
    soup = BeautifulSoup(html_professional, 'html.parser')
    tone = extractor._infer_tone(soup)
    assert tone == "professional"
    
    # Casual tone
    html_casual = "<html><body>Hey awesome cool easy simple fun</body></html>"
    soup = BeautifulSoup(html_casual, 'html.parser')
    tone = extractor._infer_tone(soup)
    assert tone == "casual"


@pytest.mark.asyncio
async def test_rgb_to_hex():
    """Test RGB to hex color conversion"""
    extractor = BrandIdentityExtractor()
    
    assert extractor._rgb_to_hex("rgb(255, 87, 51)") == "#ff5733"
    assert extractor._rgb_to_hex("rgba(51, 255, 87, 0.5)") == "#33ff57"
    assert extractor._rgb_to_hex("invalid") is None


# ============================================================================
# Integration Tests - Service Clients
# ============================================================================

@pytest.mark.asyncio
async def test_syncbrain_client_generate_campaign_brief(sample_brand_identity):
    """Test SyncBrain campaign brief generation"""
    client = SyncBrainClient("http://mock-syncbrain:8001")
    
    # Mock httpx response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "planned",
        "user_id": "scraper_Example Corp",
        "plan": "Target tech professionals with innovative messaging. Focus on quality and service."
    }
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        brief = await client.generate_campaign_brief(sample_brand_identity)
        
        assert brief.campaign_id.startswith("campaign_")
        assert brief.brand_identity == sample_brand_identity
        assert "tech professionals" in brief.target_audience.lower()
        assert brief.tone_guidance == "professional"


@pytest.mark.asyncio
async def test_synccreate_client_generate_ad_variations(sample_campaign_brief):
    """Test SyncCreate ad variation generation"""
    client = SyncCreateClient("http://mock-synccreate:8004")
    
    # Mock httpx response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "creative_id": "creative_123",
        "creative_url": "Generated ad copy here"
    }
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        assets = await client.generate_ad_variations(sample_campaign_brief, num_copies=2, num_image_prompts=2)
        
        assert len(assets["copies"]) == 2
        assert len(assets["image_prompts"]) == 2
        assert all(a.asset_type == "copy" for a in assets["copies"])
        assert all(a.asset_type == "image_prompt" for a in assets["image_prompts"])


@pytest.mark.asyncio
async def test_syncshield_client_validate_asset(sample_brand_identity):
    """Test SyncShield asset validation"""
    client = SyncShieldClient("http://mock-syncshield:8006")
    
    # Test brand-safe asset
    safe_asset = GeneratedAsset(
        asset_id="asset_1",
        asset_type="copy",
        content="Discover our amazing quality products and excellent service for innovation."
    )
    
    validated = await client.validate_asset(safe_asset, sample_brand_identity)
    
    assert validated.brand_safe == True
    assert validated.sentiment_score > 0.5
    assert validated.compliance_status == "approved"
    
    # Test unsafe asset
    unsafe_asset = GeneratedAsset(
        asset_id="asset_2",
        asset_type="copy",
        content="This is a hateful and offensive scam message."
    )
    
    validated = await client.validate_asset(unsafe_asset, sample_brand_identity)
    
    assert validated.brand_safe == False
    assert validated.compliance_status == "rejected"


# ============================================================================
# Integration Tests - Orchestrator
# ============================================================================

@pytest.mark.asyncio
async def test_orchestrator_execute_full_workflow(sample_brand_identity, sample_campaign_brief):
    """Test complete SyncScrape workflow orchestration"""
    orchestrator = SyncScrapeOrchestrator(
        syncbrain_url="http://mock-syncbrain:8001",
        synccreate_url="http://mock-synccreate:8004",
        syncshield_url="http://mock-syncshield:8006"
    )
    
    # Mock the extractor
    with patch("scraper.BrandIdentityExtractor") as mock_extractor:
        mock_instance = AsyncMock()
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_instance.extract.return_value = sample_brand_identity
        mock_extractor.return_value = mock_instance
        
        # Mock SyncBrain client
        with patch.object(orchestrator.syncbrain_client, "generate_campaign_brief", new_callable=AsyncMock) as mock_brain:
            mock_brain.return_value = sample_campaign_brief
            
            # Mock SyncCreate client
            with patch.object(orchestrator.synccreate_client, "generate_ad_variations", new_callable=AsyncMock) as mock_create:
                mock_create.return_value = {
                    "copies": [
                        GeneratedAsset(asset_id="copy_1", asset_type="copy", content="Ad copy 1"),
                        GeneratedAsset(asset_id="copy_2", asset_type="copy", content="Ad copy 2")
                    ],
                    "image_prompts": [
                        GeneratedAsset(asset_id="img_1", asset_type="image_prompt", content="Image prompt 1")
                    ]
                }
                
                # Mock SyncShield client
                async def mock_validate(asset, brand_id):
                    asset.brand_safe = True
                    asset.sentiment_score = 0.8
                    asset.compliance_status = "approved"
                    return asset
                
                with patch.object(orchestrator.syncshield_client, "validate_asset", side_effect=mock_validate):
                    result = await orchestrator.execute("https://example.com", num_ad_copies=2, num_image_prompts=1)
                    
                    # Verify result structure
                    assert result["status"] == "success"
                    assert result["brand_identity"]["brand_name"] == "Example Corp"
                    assert result["campaign_brief"]["campaign_id"] == "campaign_123"
                    assert len(result["generated_assets"]["copies"]) == 2
                    assert len(result["generated_assets"]["image_prompts"]) == 1
                    
                    # Verify metrics
                    assert result["metrics"]["total_assets"] == 3
                    assert result["metrics"]["approved_assets"] == 3
                    assert result["metrics"]["approval_rate"] == 100.0


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

@pytest.mark.asyncio
async def test_syncbrain_client_handles_api_error(sample_brand_identity):
    """Test SyncBrain client handles API errors gracefully"""
    import httpx
    client = SyncBrainClient("http://mock-syncbrain:8001")
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_instance = AsyncMock()
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_instance.post = AsyncMock(side_effect=httpx.HTTPError("Network error"))
        mock_client_class.return_value = mock_instance
        
        with pytest.raises(RuntimeError, match="Failed to generate campaign brief"):
            await client.generate_campaign_brief(sample_brand_identity)


@pytest.mark.asyncio
async def test_extractor_without_context_manager():
    """Test that extractor raises error when not used as context manager"""
    extractor = BrandIdentityExtractor()
    
    with pytest.raises(RuntimeError, match="not initialized"):
        await extractor.extract("https://example.com")


def test_brand_identity_defaults():
    """Test BrandIdentity default values"""
    identity = BrandIdentity(url="https://test.com")
    
    assert identity.url == "https://test.com"
    assert identity.brand_name is None
    assert identity.primary_colors == []
    assert identity.secondary_colors == []
    assert identity.product_catalog == []
    assert isinstance(identity.extracted_at, datetime)


# ============================================================================
# Performance Tests (optional, for future optimization)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.performance
async def test_orchestrator_execution_time(sample_brand_identity, sample_campaign_brief):
    """Test that orchestration completes within reasonable time (with mocks)"""
    import time
    
    orchestrator = SyncScrapeOrchestrator()
    
    with patch("scraper.BrandIdentityExtractor") as mock_extractor:
        mock_instance = AsyncMock()
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_instance.extract.return_value = sample_brand_identity
        mock_extractor.return_value = mock_instance
        
        with patch.object(orchestrator.syncbrain_client, "generate_campaign_brief", new_callable=AsyncMock) as mock_brain:
            mock_brain.return_value = sample_campaign_brief
            
            with patch.object(orchestrator.synccreate_client, "generate_ad_variations", new_callable=AsyncMock) as mock_create:
                mock_create.return_value = {
                    "copies": [GeneratedAsset(asset_id=f"c{i}", asset_type="copy", content=f"Copy {i}") for i in range(5)],
                    "image_prompts": [GeneratedAsset(asset_id=f"i{i}", asset_type="image_prompt", content=f"Img {i}") for i in range(3)]
                }
                
                async def mock_validate(asset, brand_id):
                    asset.brand_safe = True
                    asset.sentiment_score = 0.8
                    asset.compliance_status = "approved"
                    return asset
                
                with patch.object(orchestrator.syncshield_client, "validate_asset", side_effect=mock_validate):
                    start = time.time()
                    await orchestrator.execute("https://example.com")
                    duration = time.time() - start
                    
                    # Should complete in under 1 second with mocks
                    assert duration < 1.0, f"Orchestration took {duration:.2f}s, expected < 1.0s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
