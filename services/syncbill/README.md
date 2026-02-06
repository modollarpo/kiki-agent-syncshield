# SyncBill - Automated Billing & Settlement Service

The financial engine for KIKI Agent™ OaaS (Outcomes-as-a-Service) platform. Calculates performance-based fees, generates comprehensive QBR reports, and ensures transparent financial reconciliation.

## Overview

SyncBill implements the core OaaS business model: **No Uplift = No Fee**

- Calculates revenue uplift by comparing actual performance against baseline
- Applies 20% success fee only on positive uplift
- Generates professional Quarterly Business Review (QBR) PDF reports
- Integrates with SyncValue (performance metrics) and SyncShield (audit logging)
- Full REST API with OpenTelemetry tracing and Prometheus metrics

## Architecture

```
SyncBill Service
├── Domain Layer
│   ├── RevenueData - Billing period data model
│   ├── SettlementResult - Calculated settlement
│   └── QBRRequest/Response - Report generation
├── Service Layer
│   ├── SettlementService - OaaS fee calculation
│   ├── QBRReportService - PDF report generation
│   ├── SyncValueClient - Performance metrics integration
│   └── SyncShieldClient - Audit logging integration
└── API Layer
    ├── POST /api/v1/settlement/calculate
    ├── GET /api/v1/settlement/{id}
    ├── GET /api/v1/settlements
    ├── POST /api/v1/qbr/generate
    └── GET /api/v1/reports/{id}/download
```

## Key Features

### 1. Performance-Based Settlement
- **Core Rule**: Zero fee if no revenue uplift
- **Success Fee**: 20% of (Total Revenue - Baseline Revenue)
- **Transparent**: Full breakdown of uplift, fee, and client benefit

### 2. QBR Report Generation
- Professional PDF reports with financial summary
- Integration with SyncValue for performance metrics
- Automated retention and expiration management

### 3. Service Integrations
- **SyncValue**: Fetch performance metrics and attribution data
- **SyncShield**: Audit logging for compliance and transparency

### 4. Enterprise Features
- Request ID tracking for debugging
- Prometheus metrics (`/metrics`)
- Health checks (`/health`)
- OpenTelemetry distributed tracing

## API Endpoints

### Calculate Settlement
```bash
POST /api/v1/settlement/calculate
Content-Type: application/json

{
  "client_id": "client_abc123",
  "billing_cycle": "Q1 2026",
  "total_revenue": 150000.0,
  "baseline_revenue": 100000.0,
  "attribution_source": "syncvalue"
}

# Response
{
  "settlement_id": "settlement_xyz789",
  "client_id": "client_abc123",
  "billing_cycle": "Q1 2026",
  "total_revenue": 150000.0,
  "baseline_revenue": 100000.0,
  "attributed_uplift": 50000.0,
  "success_fee_rate": 0.2,
  "kiki_success_fee": 10000.0,
  "client_net_benefit": 40000.0,
  "status": "SETTLEMENT_CALCULATED",
  "calculated_at": "2026-01-15T10:30:00Z",
  "audit_logged": true
}
```

### Generate QBR Report
```bash
POST /api/v1/qbr/generate
Content-Type: application/json

{
  "client_name": "Acme Corp",
  "client_id": "client_abc123",
  "period": "Q1 2026",
  "include_metrics": true
}

# Response
{
  "report_id": "qbr_abc123",
  "client_name": "Acme Corp",
  "period": "Q1 2026",
  "file_path": "/tmp/kiki_reports/qbr_client_abc123_Q1_2026_abc123.pdf",
  "download_url": "/api/v1/reports/qbr_abc123/download",
  "generated_at": "2026-01-15T11:00:00Z",
  "expires_at": "2026-04-15T11:00:00Z"
}
```

### Download Report
```bash
GET /api/v1/reports/{report_id}/download

# Returns PDF file
```

## Installation & Setup

### Local Development
```bash
# Install dependencies
cd services/syncbill
pip install -r requirements.txt

# Run the service
python app/main.py

# Service runs on http://localhost:8008
```

### Docker
```bash
# Build image
docker build -t syncbill:latest -f services/syncbill/Dockerfile .

# Run container
docker run -p 8008:8008 \
  -e SYNCVALUE_URL=http://syncvalue:8002 \
  -e SYNCSHIELD_URL=http://syncshield:8006 \
  syncbill:latest
```

### docker-compose
```bash
# Start all services
docker-compose up syncbill

# SyncBill depends on SyncValue and SyncShield
```

## Configuration

Environment variables:
```bash
# Service Configuration
SERVICE_NAME=syncbill
PORT=8008
LOG_LEVEL=INFO

# Billing Settings
SUCCESS_FEE_RATE=0.20          # 20% success fee
MINIMUM_UPLIFT_THRESHOLD=0.0    # No fee if uplift ≤ 0

# Report Settings
REPORTS_DIR=/tmp/kiki_reports
REPORT_RETENTION_DAYS=90

# Service Integration
SYNCVALUE_URL=http://syncvalue:8002
SYNCSHIELD_URL=http://syncshield:8006
```

## Testing

```bash
# Run all tests
pytest services/syncbill/tests/ -v

# Run with coverage
pytest services/syncbill/tests/ --cov=app --cov-report=html

# Run specific test
pytest services/syncbill/tests/test_syncbill.py::test_settlement_with_uplift -v
```

## Settlement Calculation Logic

### Example 1: Positive Uplift
```
Total Revenue:    $150,000
Baseline Revenue: $100,000
─────────────────────────────
Uplift:           $ 50,000
KIKI Fee (20%):   $ 10,000
Client Benefit:   $ 40,000
```

### Example 2: No Uplift
```
Total Revenue:    $ 95,000
Baseline Revenue: $100,000
─────────────────────────────
Uplift:           $ -5,000
KIKI Fee:         $      0   ← No uplift = No fee
Client Benefit:   $      0
```

## Integration Examples

### Python Client
```python
import httpx

async def calculate_settlement(client_id: str, revenue: float, baseline: float):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://syncbill:8008/api/v1/settlement/calculate",
            json={
                "client_id": client_id,
                "billing_cycle": "Q1 2026",
                "total_revenue": revenue,
                "baseline_revenue": baseline
            }
        )
        return response.json()

# Usage
settlement = await calculate_settlement("client_123", 150000.0, 100000.0)
print(f"KIKI Fee: ${settlement['kiki_success_fee']:,.2f}")
print(f"Client Benefit: ${settlement['client_net_benefit']:,.2f}")
```

### JavaScript/Node.js Client
```javascript
const fetch = require('node-fetch');

async function calculateSettlement(clientId, revenue, baseline) {
  const response = await fetch('http://syncbill:8008/api/v1/settlement/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      client_id: clientId,
      billing_cycle: 'Q1 2026',
      total_revenue: revenue,
      baseline_revenue: baseline
    })
  });
  return await response.json();
}

// Usage
const settlement = await calculateSettlement('client_123', 150000, 100000);
console.log(`KIKI Fee: $${settlement.kiki_success_fee.toLocaleString()}`);
```

## Monitoring & Observability

### Prometheus Metrics
```bash
curl http://localhost:8008/metrics

# Key metrics:
# - syncbill_requests_total
# - syncbill_settlements_total
# - syncbill_qbr_reports_total
# - syncbill_errors_total
# - syncbill_request_latency_seconds
```

### Health Check
```bash
curl http://localhost:8008/health

{
  "status": "healthy",
  "service": "syncbill",
  "version": "1.0.0",
  "metrics": {
    "settlements_processed": 42,
    "qbr_reports_generated": 18
  }
}
```

## Troubleshooting

### Issue: QBR generation fails
**Solution**: Ensure fpdf library is installed: `pip install fpdf`

### Issue: SyncValue integration fails
**Solution**: Check SYNCVALUE_URL is correct and service is running

### Issue: Reports directory not writable
**Solution**: Ensure REPORTS_DIR has write permissions or set to writable path

## File Structure

```
services/syncbill/
├── app/
│   └── main.py           # Main FastAPI application (650+ lines)
├── logic/
│   ├── settlement.js     # Legacy JS logic (reference only)
│   └── qbr_report.py     # Legacy Python logic (reference only)
├── tests/
│   └── test_syncbill.py  # Comprehensive test suite
├── Dockerfile
├── requirements.txt
└── README.md
```

## Related Services

- **SyncValue**: Provides performance metrics and revenue attribution
- **SyncShield**: Audit logging and compliance tracking
- **SyncBrain**: Strategic planning and campaign management

## License

Part of KIKI Agent™ platform. See main repository for licensing.
