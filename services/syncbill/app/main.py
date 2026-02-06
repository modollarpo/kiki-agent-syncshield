"""
SyncBill - Automated Billing & Settlement Service

The financial engine for KIKI Agent™ OaaS platform. Calculates performance-based
fees, generates QBR reports, and ensures transparent financial reconciliation.

Architecture: Clean Architecture + DDD
Features:
- OaaS settlement calculation (20% success fee on uplift)
- Automated QBR PDF report generation
- Integration with SyncValue (performance metrics) and SyncShield (audit)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from fastapi import FastAPI, HTTPException, Response, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, validator
from typing import Any, Dict, List, Optional
import httpx
import logging
from datetime import datetime, timedelta
from pathlib import Path
import uuid

# Enterprise components
from shared.middleware import RequestIDMiddleware, RequestLoggingMiddleware
from shared.config import ServiceConfig
from shared.health import HealthChecker, HealthStatus, ServiceHealth

# Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# OpenTelemetry tracing
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# PDF generation
try:
    from fpdf import FPDF
except ImportError:
    FPDF = None  # Will be installed via requirements.txt


# ============================================================================
# Configuration
# ============================================================================

class SyncBillConfig(ServiceConfig):
    """SyncBill-specific configuration"""
    service_name: str = "syncbill"
    port: int = 8008
    
    # Billing settings
    success_fee_rate: float = 0.20  # 20% of uplift
    minimum_uplift_threshold: float = 0.0  # No fee if no uplift
    
    # Report settings
    reports_dir: str = "/tmp/kiki_reports"
    report_retention_days: int = 90
    
    # Service URLs
    syncvalue_url: str = "http://syncvalue:8002"
    syncshield_url: str = "http://syncshield:8006"


config = SyncBillConfig()

# Configure logging
logging.basicConfig(
    level=config.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("syncbill")

# Create reports directory
Path(config.reports_dir).mkdir(parents=True, exist_ok=True)


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="SyncBill - Automated Billing & Settlement",
    description="OaaS financial engine with performance-based settlement and QBR automation",
    version=config.version
)

# Add middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestLoggingMiddleware, logger=logger)

# Initialize health checker
health_checker = HealthChecker(service_name=config.service_name, version=config.version)

# OpenTelemetry instrumentation
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
FastAPIInstrumentor.instrument_app(app)
span_processor = BatchSpanProcessor(ConsoleSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

# Prometheus metrics
REQUEST_COUNT = Counter("syncbill_requests_total", "Total requests", ["endpoint", "method"])
ERROR_COUNT = Counter("syncbill_errors_total", "Total errors", ["endpoint"])
SETTLEMENTS_PROCESSED = Counter("syncbill_settlements_total", "Total settlements processed")
QBR_REPORTS_GENERATED = Counter("syncbill_qbr_reports_total", "Total QBR reports generated")
REQUEST_LATENCY = Histogram("syncbill_request_latency_seconds", "Request latency", ["endpoint"])


# ============================================================================
# Domain Models
# ============================================================================

class RevenueData(BaseModel):
    """Revenue data for a billing period"""
    client_id: str = Field(..., description="Client identifier")
    billing_cycle: str = Field(..., description="Billing period (e.g., 'Q1 2026', 'Jan 2026')")
    total_revenue: float = Field(..., gt=0, description="Total revenue for the period")
    baseline_revenue: float = Field(..., ge=0, description="Historical baseline revenue")
    attribution_source: Optional[str] = Field(default="manual", description="Data source (syncvalue, manual)")
    
    @validator('billing_cycle')
    def validate_billing_cycle(cls, v):
        if not v or len(v) < 3:
            raise ValueError("Billing cycle must be a valid period identifier")
        return v


class SettlementResult(BaseModel):
    """Settlement calculation result"""
    settlement_id: str = Field(..., description="Unique settlement identifier")
    client_id: str
    billing_cycle: str
    total_revenue: float
    baseline_revenue: float
    attributed_uplift: float = Field(..., description="Revenue uplift attributed to KIKI Agent")
    success_fee_rate: float = Field(..., description="Applied success fee percentage")
    kiki_success_fee: float = Field(..., description="KIKI Agent fee amount")
    client_net_benefit: float = Field(..., description="Client's net benefit after fee")
    status: str = Field(..., description="Settlement status")
    calculated_at: datetime
    audit_logged: bool = Field(default=False, description="Whether logged to SyncShield")


class QBRRequest(BaseModel):
    """QBR report generation request"""
    client_name: str = Field(..., description="Client company name")
    client_id: str = Field(..., description="Client identifier")
    period: str = Field(..., description="Reporting period (e.g., 'Q1 2026')")
    include_metrics: bool = Field(default=True, description="Include performance metrics from SyncValue")


class QBRResponse(BaseModel):
    """QBR report generation response"""
    report_id: str
    client_name: str
    period: str
    file_path: str
    download_url: str
    generated_at: datetime
    expires_at: datetime


# ============================================================================
# Service Layer - Settlement Logic
# ============================================================================

class SettlementService:
    """Service for calculating OaaS settlements"""
    
    def __init__(self, config: SyncBillConfig):
        self.config = config
        self.settlements_store: Dict[str, SettlementResult] = {}
    
    def calculate_settlement(self, revenue_data: RevenueData) -> SettlementResult:
        """
        Calculate OaaS settlement based on performance uplift.
        
        Core Rule: No Uplift = No Fee
        Fee = 20% of (Total Revenue - Baseline Revenue)
        """
        logger.info(f"Calculating settlement for client {revenue_data.client_id}, cycle {revenue_data.billing_cycle}")
        
        # Calculate uplift
        uplift = revenue_data.total_revenue - revenue_data.baseline_revenue
        
        # Apply OaaS rule: No uplift = No fee
        if uplift <= self.config.minimum_uplift_threshold:
            logger.info(f"No uplift detected ({uplift:.2f}). Zero fee applied.")
            settlement = SettlementResult(
                settlement_id=f"settlement_{uuid.uuid4().hex[:12]}",
                client_id=revenue_data.client_id,
                billing_cycle=revenue_data.billing_cycle,
                total_revenue=revenue_data.total_revenue,
                baseline_revenue=revenue_data.baseline_revenue,
                attributed_uplift=uplift,
                success_fee_rate=0.0,
                kiki_success_fee=0.0,
                client_net_benefit=0.0,
                status="NO_UPLIFT_DETECTED",
                calculated_at=datetime.utcnow()
            )
        else:
            # Calculate success fee
            fee_amount = uplift * self.config.success_fee_rate
            net_benefit = uplift - fee_amount
            
            logger.info(
                f"Uplift: ${uplift:,.2f}, "
                f"Fee ({self.config.success_fee_rate*100}%): ${fee_amount:,.2f}, "
                f"Client Benefit: ${net_benefit:,.2f}"
            )
            
            settlement = SettlementResult(
                settlement_id=f"settlement_{uuid.uuid4().hex[:12]}",
                client_id=revenue_data.client_id,
                billing_cycle=revenue_data.billing_cycle,
                total_revenue=revenue_data.total_revenue,
                baseline_revenue=revenue_data.baseline_revenue,
                attributed_uplift=uplift,
                success_fee_rate=self.config.success_fee_rate,
                kiki_success_fee=fee_amount,
                client_net_benefit=net_benefit,
                status="SETTLEMENT_CALCULATED",
                calculated_at=datetime.utcnow()
            )
        
        # Store settlement
        self.settlements_store[settlement.settlement_id] = settlement
        
        SETTLEMENTS_PROCESSED.inc()
        return settlement
    
    def get_settlement(self, settlement_id: str) -> Optional[SettlementResult]:
        """Retrieve a settlement by ID"""
        return self.settlements_store.get(settlement_id)
    
    def list_settlements(self, client_id: Optional[str] = None) -> List[SettlementResult]:
        """List all settlements, optionally filtered by client"""
        settlements = list(self.settlements_store.values())
        if client_id:
            settlements = [s for s in settlements if s.client_id == client_id]
        return settlements


# ============================================================================
# Service Layer - QBR Report Generation
# ============================================================================

class QBRReportService:
    """Service for generating Quarterly Business Review reports"""
    
    def __init__(self, config: SyncBillConfig):
        self.config = config
    
    def generate_report(
        self,
        client_name: str,
        client_id: str,
        period: str,
        settlement: SettlementResult,
        metrics: Optional[Dict[str, Any]] = None
    ) -> QBRResponse:
        """Generate a PDF QBR report"""
        if FPDF is None:
            raise RuntimeError("FPDF library not installed. Run: pip install fpdf")
        
        logger.info(f"Generating QBR report for {client_name}, period {period}")
        
        # Generate unique report ID
        report_id = f"qbr_{uuid.uuid4().hex[:12]}"
        filename = f"qbr_{client_id}_{period.replace(' ', '_')}_{report_id}.pdf"
        file_path = os.path.join(self.config.reports_dir, filename)
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", 'B', 20)
        pdf.cell(0, 15, "KIKI Agent", ln=True, align='C')
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Quarterly Business Review", ln=True, align='C')
        pdf.ln(10)
        
        # Client Information
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, f"Client: {client_name}", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"Period: {period}", ln=True)
        pdf.cell(0, 8, f"Report ID: {report_id}", ln=True)
        pdf.ln(10)
        
        # Financial Summary
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Financial Summary", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"Total Revenue: ${settlement.total_revenue:,.2f}", ln=True)
        pdf.cell(0, 8, f"Baseline Revenue: ${settlement.baseline_revenue:,.2f}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, f"Attributed Uplift: ${settlement.attributed_uplift:,.2f}", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"KIKI Success Fee ({settlement.success_fee_rate*100}%): ${settlement.kiki_success_fee:,.2f}", ln=True)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, f"Your Net Benefit: ${settlement.client_net_benefit:,.2f}", ln=True)
        pdf.ln(10)
        
        # Performance Metrics (if available)
        if metrics:
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "Performance Metrics", ln=True)
            pdf.set_font("Arial", '', 11)
            
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    pdf.cell(0, 7, f"{key}: {value:,.2f}", ln=True)
                else:
                    pdf.cell(0, 7, f"{key}: {value}", ln=True)
            pdf.ln(10)
        
        # Status & Notes
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Settlement Status", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"Status: {settlement.status}", ln=True)
        pdf.cell(0, 8, f"Calculated: {settlement.calculated_at.strftime('%Y-%m-%d %H:%M UTC')}", ln=True)
        pdf.ln(15)
        
        # Footer
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 8, "KIKI Agent - Autonomous Revenue Engine", ln=True, align='C')
        pdf.cell(0, 8, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ln=True, align='C')
        
        # Save PDF
        pdf.output(file_path)
        
        logger.info(f"QBR report generated: {file_path}")
        QBR_REPORTS_GENERATED.inc()
        
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(days=self.config.report_retention_days)
        
        return QBRResponse(
            report_id=report_id,
            client_name=client_name,
            period=period,
            file_path=file_path,
            download_url=f"/api/v1/reports/{report_id}/download",
            generated_at=datetime.utcnow(),
            expires_at=expires_at
        )


# ============================================================================
# Service Integration Layer
# ============================================================================

class SyncValueClient:
    """Client for fetching performance metrics from SyncValue"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def get_client_metrics(self, client_id: str, period: str) -> Dict[str, Any]:
        """Fetch client performance metrics"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/metrics", params={"client_id": client_id, "period": period})
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.warning(f"Failed to fetch SyncValue metrics: {e}")
        
        return {"status": "unavailable"}


class SyncShieldClient:
    """Client for audit logging to SyncShield"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def log_settlement(self, settlement: SettlementResult) -> bool:
        """Log settlement to SyncShield for audit trail"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                audit_data = {
                    "event": "settlement_calculated",
                    "settlement_id": settlement.settlement_id,
                    "client_id": settlement.client_id,
                    "billing_cycle": settlement.billing_cycle,
                    "kiki_fee": settlement.kiki_success_fee,
                    "timestamp": settlement.calculated_at.isoformat()
                }
                response = await client.post(f"{self.base_url}/audit", json=audit_data)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to log to SyncShield: {e}")
            return False


# ============================================================================
# Initialize Services
# ============================================================================

settlement_service = SettlementService(config)
qbr_service = QBRReportService(config)
syncvalue_client = SyncValueClient(config.syncvalue_url)
syncshield_client = SyncShieldClient(config.syncshield_url)


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health", response_model=ServiceHealth, tags=["monitoring"])
async def health():
    """Health check endpoint"""
    metrics = {
        "settlements_processed": SETTLEMENTS_PROCESSED._value.get(),
        "qbr_reports_generated": QBR_REPORTS_GENERATED._value.get(),
        "reports_dir": config.reports_dir
    }
    return await health_checker.get_health(metrics=metrics)


@app.get("/metrics", tags=["monitoring"])
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/settlement/calculate", response_model=SettlementResult, tags=["settlement"])
async def calculate_settlement(revenue_data: RevenueData, background_tasks: BackgroundTasks):
    """
    Calculate OaaS settlement for a billing period.
    
    Core Rule: No Uplift = No Fee
    - Calculates revenue uplift (Total - Baseline)
    - Applies 20% success fee on positive uplift
    - Logs to SyncShield for audit trail
    """
    REQUEST_COUNT.labels(endpoint="/settlement/calculate", method="POST").inc()
    
    with REQUEST_LATENCY.labels(endpoint="/settlement/calculate").time():
        with tracer.start_as_current_span("calculate_settlement"):
            try:
                # Calculate settlement
                settlement = settlement_service.calculate_settlement(revenue_data)
                
                # Log to SyncShield in background
                async def log_audit():
                    logged = await syncshield_client.log_settlement(settlement)
                    if logged:
                        settlement.audit_logged = True
                        logger.info(f"Settlement {settlement.settlement_id} logged to SyncShield")
                
                background_tasks.add_task(log_audit)
                
                logger.info(f"Settlement calculated: {settlement.settlement_id}")
                return settlement
                
            except Exception as e:
                logger.error(f"Error calculating settlement: {e}", exc_info=True)
                ERROR_COUNT.labels(endpoint="/settlement/calculate").inc()
                raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/settlement/{settlement_id}", response_model=SettlementResult, tags=["settlement"])
def get_settlement(settlement_id: str):
    """Retrieve a settlement by ID"""
    REQUEST_COUNT.labels(endpoint="/settlement/{id}", method="GET").inc()
    
    settlement = settlement_service.get_settlement(settlement_id)
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found")
    
    return settlement


@app.get("/api/v1/settlements", response_model=List[SettlementResult], tags=["settlement"])
def list_settlements(client_id: Optional[str] = None):
    """List all settlements, optionally filtered by client"""
    REQUEST_COUNT.labels(endpoint="/settlements", method="GET").inc()
    return settlement_service.list_settlements(client_id)


@app.post("/api/v1/qbr/generate", response_model=QBRResponse, tags=["reports"])
async def generate_qbr(request: QBRRequest):
    """
    Generate a Quarterly Business Review (QBR) PDF report.
    
    Includes:
    - Financial summary and settlement details
    - Performance metrics from SyncValue (if requested)
    - Downloadable PDF report
    """
    REQUEST_COUNT.labels(endpoint="/qbr/generate", method="POST").inc()
    
    with REQUEST_LATENCY.labels(endpoint="/qbr/generate").time():
        with tracer.start_as_current_span("generate_qbr"):
            try:
                # Find most recent settlement for this client
                client_settlements = settlement_service.list_settlements(request.client_id)
                if not client_settlements:
                    raise HTTPException(
                        status_code=404,
                        detail=f"No settlements found for client {request.client_id}"
                    )
                
                # Use most recent settlement
                settlement = max(client_settlements, key=lambda s: s.calculated_at)
                
                # Fetch metrics from SyncValue if requested
                metrics = None
                if request.include_metrics:
                    metrics = await syncvalue_client.get_client_metrics(request.client_id, request.period)
                
                # Generate report
                qbr_response = qbr_service.generate_report(
                    client_name=request.client_name,
                    client_id=request.client_id,
                    period=request.period,
                    settlement=settlement,
                    metrics=metrics
                )
                
                logger.info(f"QBR report generated: {qbr_response.report_id}")
                return qbr_response
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error generating QBR: {e}", exc_info=True)
                ERROR_COUNT.labels(endpoint="/qbr/generate").inc()
                raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/reports/{report_id}/download", tags=["reports"])
def download_report(report_id: str):
    """Download a generated QBR report"""
    REQUEST_COUNT.labels(endpoint="/reports/download", method="GET").inc()
    
    # Find report file
    report_files = list(Path(config.reports_dir).glob(f"qbr_*_{report_id}.pdf"))
    if not report_files:
        raise HTTPException(status_code=404, detail="Report not found")
    
    file_path = report_files[0]
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=file_path.name
    )


# ============================================================================
# Startup & Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize service on startup"""
    logger.info(f"SyncBill service starting on port {config.port}")
    logger.info(f"Success fee rate: {config.success_fee_rate*100}%")
    logger.info(f"Reports directory: {config.reports_dir}")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("SyncBill service shutting down")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.port)
