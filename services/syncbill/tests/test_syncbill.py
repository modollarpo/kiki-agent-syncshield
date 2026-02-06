"""
Comprehensive test suite for SyncBill service

Tests settlement calculation, QBR generation, service integrations, and error handling.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import httpx

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from services.syncbill.app.main import (
    app,
    RevenueData,
    SettlementResult,
    QBRRequest,
    QBRResponse,
    SettlementService,
    QBRReportService,
    SyncBillConfig,
    SyncValueClient,
    SyncShieldClient
)

from fastapi.testclient import TestClient


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def test_config():
    """Test configuration"""
    return SyncBillConfig(
        service_name="syncbill-test",
        port=8008,
        success_fee_rate=0.20,
        reports_dir="/tmp/kiki_reports_test",
        syncvalue_url="http://syncvalue-test:8002",
        syncshield_url="http://syncshield-test:8006"
    )


@pytest.fixture
def settlement_service(test_config):
    """Settlement service instance"""
    return SettlementService(test_config)


@pytest.fixture
def qbr_service(test_config):
    """QBR report service instance"""
    Path(test_config.reports_dir).mkdir(parents=True, exist_ok=True)
    return QBRReportService(test_config)


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def sample_revenue_data():
    """Sample revenue data with uplift"""
    return RevenueData(
        client_id="client_abc123",
        billing_cycle="Q1 2026",
        total_revenue=150000.0,
        baseline_revenue=100000.0,
        attribution_source="syncvalue"
    )


@pytest.fixture
def sample_revenue_no_uplift():
    """Sample revenue data with no uplift"""
    return RevenueData(
        client_id="client_xyz789",
        billing_cycle="Q1 2026",
        total_revenue=95000.0,
        baseline_revenue=100000.0,
        attribution_source="manual"
    )


@pytest.fixture
def sample_settlement():
    """Sample settlement result"""
    return SettlementResult(
        settlement_id="settlement_abc123",
        client_id="client_abc123",
        billing_cycle="Q1 2026",
        total_revenue=150000.0,
        baseline_revenue=100000.0,
        attributed_uplift=50000.0,
        success_fee_rate=0.20,
        kiki_success_fee=10000.0,
        client_net_benefit=40000.0,
        status="SETTLEMENT_CALCULATED",
        calculated_at=datetime.utcnow(),
        audit_logged=False
    )


# ============================================================================
# Domain Model Tests
# ============================================================================

def test_revenue_data_validation():
    """Test RevenueData validation"""
    # Valid data
    revenue = RevenueData(
        client_id="test_client",
        billing_cycle="Q1 2026",
        total_revenue=100000.0,
        baseline_revenue=80000.0
    )
    assert revenue.client_id == "test_client"
    assert revenue.total_revenue == 100000.0
    
    # Invalid billing cycle
    with pytest.raises(ValueError):
        RevenueData(
            client_id="test",
            billing_cycle="",
            total_revenue=100000.0,
            baseline_revenue=80000.0
        )
    
    # Negative revenue should fail
    with pytest.raises(ValueError):
        RevenueData(
            client_id="test",
            billing_cycle="Q1 2026",
            total_revenue=-1000.0,
            baseline_revenue=80000.0
        )


def test_settlement_result_structure(sample_settlement):
    """Test SettlementResult structure"""
    assert sample_settlement.settlement_id.startswith("settlement_")
    assert sample_settlement.attributed_uplift == 50000.0
    assert sample_settlement.kiki_success_fee == 10000.0
    assert sample_settlement.client_net_benefit == 40000.0
    assert sample_settlement.status == "SETTLEMENT_CALCULATED"


# ============================================================================
# Settlement Service Tests
# ============================================================================

def test_settlement_with_uplift(settlement_service, sample_revenue_data):
    """Test settlement calculation with positive uplift"""
    result = settlement_service.calculate_settlement(sample_revenue_data)
    
    # Verify calculations
    expected_uplift = 150000.0 - 100000.0  # 50,000
    expected_fee = expected_uplift * 0.20  # 10,000
    expected_benefit = expected_uplift - expected_fee  # 40,000
    
    assert result.attributed_uplift == expected_uplift
    assert result.kiki_success_fee == expected_fee
    assert result.client_net_benefit == expected_benefit
    assert result.status == "SETTLEMENT_CALCULATED"
    assert result.success_fee_rate == 0.20


def test_settlement_no_uplift(settlement_service, sample_revenue_no_uplift):
    """Test settlement calculation with no uplift (zero fee)"""
    result = settlement_service.calculate_settlement(sample_revenue_no_uplift)
    
    # Core OaaS rule: No uplift = No fee
    assert result.attributed_uplift < 0
    assert result.kiki_success_fee == 0.0
    assert result.client_net_benefit == 0.0
    assert result.status == "NO_UPLIFT_DETECTED"
    assert result.success_fee_rate == 0.0


def test_settlement_storage(settlement_service, sample_revenue_data):
    """Test settlement storage and retrieval"""
    # Calculate settlement
    result = settlement_service.calculate_settlement(sample_revenue_data)
    
    # Retrieve by ID
    retrieved = settlement_service.get_settlement(result.settlement_id)
    assert retrieved is not None
    assert retrieved.settlement_id == result.settlement_id
    assert retrieved.client_id == result.client_id
    
    # Non-existent ID
    missing = settlement_service.get_settlement("nonexistent_id")
    assert missing is None


def test_list_settlements(settlement_service, sample_revenue_data, sample_revenue_no_uplift):
    """Test listing settlements with filtering"""
    # Create multiple settlements
    settlement1 = settlement_service.calculate_settlement(sample_revenue_data)
    settlement2 = settlement_service.calculate_settlement(sample_revenue_no_uplift)
    
    # List all settlements
    all_settlements = settlement_service.list_settlements()
    assert len(all_settlements) >= 2
    
    # Filter by client
    client_settlements = settlement_service.list_settlements(client_id="client_abc123")
    assert len(client_settlements) >= 1
    assert all(s.client_id == "client_abc123" for s in client_settlements)


# ============================================================================
# QBR Report Service Tests
# ============================================================================

def test_qbr_generation(qbr_service, sample_settlement):
    """Test QBR PDF report generation"""
    response = qbr_service.generate_report(
        client_name="Acme Corp",
        client_id="client_abc123",
        period="Q1 2026",
        settlement=sample_settlement,
        metrics={"conversion_rate": 0.15, "roas": 3.5}
    )
    
    # Verify response
    assert response.report_id.startswith("qbr_")
    assert response.client_name == "Acme Corp"
    assert response.period == "Q1 2026"
    assert response.file_path.endswith(".pdf")
    assert os.path.exists(response.file_path)
    
    # Verify expiration is set correctly
    expected_expiry = datetime.utcnow() + timedelta(days=90)
    assert abs((response.expires_at - expected_expiry).total_seconds()) < 60


def test_qbr_without_metrics(qbr_service, sample_settlement):
    """Test QBR generation without performance metrics"""
    response = qbr_service.generate_report(
        client_name="Acme Corp",
        client_id="client_abc123",
        period="Q1 2026",
        settlement=sample_settlement,
        metrics=None
    )
    
    assert response.report_id is not None
    assert os.path.exists(response.file_path)


# ============================================================================
# Service Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_syncvalue_client_success():
    """Test SyncValue client successful metrics fetch"""
    client = SyncValueClient("http://syncvalue-test:8002")
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"conversion_rate": 0.15, "roas": 3.5}
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        metrics = await client.get_client_metrics("client_123", "Q1 2026")
        assert metrics["conversion_rate"] == 0.15
        assert metrics["roas"] == 3.5


@pytest.mark.asyncio
async def test_syncvalue_client_failure():
    """Test SyncValue client handles failures gracefully"""
    client = SyncValueClient("http://syncvalue-test:8002")
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(side_effect=httpx.HTTPError("Connection error"))
        
        metrics = await client.get_client_metrics("client_123", "Q1 2026")
        assert metrics["status"] == "unavailable"


@pytest.mark.asyncio
async def test_syncshield_client_success():
    """Test SyncShield client successful audit logging"""
    client = SyncShieldClient("http://syncshield-test:8006")
    
    mock_response = Mock()
    mock_response.status_code = 200
    
    settlement = SettlementResult(
        settlement_id="test_settlement",
        client_id="client_123",
        billing_cycle="Q1 2026",
        total_revenue=150000.0,
        baseline_revenue=100000.0,
        attributed_uplift=50000.0,
        success_fee_rate=0.20,
        kiki_success_fee=10000.0,
        client_net_benefit=40000.0,
        status="SETTLEMENT_CALCULATED",
        calculated_at=datetime.utcnow()
    )
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await client.log_settlement(settlement)
        assert result is True


@pytest.mark.asyncio
async def test_syncshield_client_failure():
    """Test SyncShield client handles failures gracefully"""
    client = SyncShieldClient("http://syncshield-test:8006")
    
    settlement = SettlementResult(
        settlement_id="test_settlement",
        client_id="client_123",
        billing_cycle="Q1 2026",
        total_revenue=150000.0,
        baseline_revenue=100000.0,
        attributed_uplift=50000.0,
        success_fee_rate=0.20,
        kiki_success_fee=10000.0,
        client_net_benefit=40000.0,
        status="SETTLEMENT_CALCULATED",
        calculated_at=datetime.utcnow()
    )
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(side_effect=httpx.HTTPError("Connection error"))
        
        result = await client.log_settlement(settlement)
        assert result is False


# ============================================================================
# API Endpoint Tests
# ============================================================================

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "metrics" in data


def test_calculate_settlement_endpoint(client):
    """Test POST /api/v1/settlement/calculate"""
    payload = {
        "client_id": "client_test123",
        "billing_cycle": "Q1 2026",
        "total_revenue": 200000.0,
        "baseline_revenue": 150000.0,
        "attribution_source": "syncvalue"
    }
    
    response = client.post("/api/v1/settlement/calculate", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["client_id"] == "client_test123"
    assert data["attributed_uplift"] == 50000.0
    assert data["kiki_success_fee"] == 10000.0
    assert data["status"] == "SETTLEMENT_CALCULATED"


def test_calculate_settlement_no_uplift_endpoint(client):
    """Test settlement calculation with no uplift via API"""
    payload = {
        "client_id": "client_test456",
        "billing_cycle": "Q1 2026",
        "total_revenue": 80000.0,
        "baseline_revenue": 100000.0
    }
    
    response = client.post("/api/v1/settlement/calculate", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["kiki_success_fee"] == 0.0
    assert data["status"] == "NO_UPLIFT_DETECTED"


def test_get_settlement_endpoint(client):
    """Test GET /api/v1/settlement/{settlement_id}"""
    # First create a settlement
    payload = {
        "client_id": "client_test789",
        "billing_cycle": "Q1 2026",
        "total_revenue": 120000.0,
        "baseline_revenue": 100000.0
    }
    
    create_response = client.post("/api/v1/settlement/calculate", json=payload)
    settlement_id = create_response.json()["settlement_id"]
    
    # Retrieve it
    get_response = client.get(f"/api/v1/settlement/{settlement_id}")
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["settlement_id"] == settlement_id


def test_get_settlement_not_found(client):
    """Test GET settlement with invalid ID"""
    response = client.get("/api/v1/settlement/nonexistent_id")
    assert response.status_code == 404


def test_list_settlements_endpoint(client):
    """Test GET /api/v1/settlements"""
    response = client.get("/api/v1/settlements")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_generate_qbr_endpoint(client):
    """Test POST /api/v1/qbr/generate"""
    # First create a settlement
    settlement_payload = {
        "client_id": "client_qbr123",
        "billing_cycle": "Q1 2026",
        "total_revenue": 180000.0,
        "baseline_revenue": 150000.0
    }
    client.post("/api/v1/settlement/calculate", json=settlement_payload)
    
    # Generate QBR
    qbr_payload = {
        "client_name": "QBR Test Corp",
        "client_id": "client_qbr123",
        "period": "Q1 2026",
        "include_metrics": False
    }
    
    response = client.post("/api/v1/qbr/generate", json=qbr_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["client_name"] == "QBR Test Corp"
    assert data["report_id"].startswith("qbr_")
    assert "download_url" in data


def test_generate_qbr_no_settlement(client):
    """Test QBR generation without existing settlement"""
    qbr_payload = {
        "client_name": "No Settlement Corp",
        "client_id": "nonexistent_client",
        "period": "Q1 2026",
        "include_metrics": False
    }
    
    response = client.post("/api/v1/qbr/generate", json=qbr_payload)
    assert response.status_code == 404


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_invalid_revenue_data(client):
    """Test API with invalid revenue data"""
    payload = {
        "client_id": "test",
        "billing_cycle": "",  # Invalid
        "total_revenue": 100000.0,
        "baseline_revenue": 80000.0
    }
    
    response = client.post("/api/v1/settlement/calculate", json=payload)
    assert response.status_code == 422  # Validation error


def test_metrics_endpoint(client):
    """Test Prometheus metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "syncbill" in response.text
