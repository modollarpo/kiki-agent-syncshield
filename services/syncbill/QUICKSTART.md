# SyncBill Service - Quick Start Guide

## What is SyncBill?

SyncBill is the automated billing and settlement service for KIKI Agent™. It implements the core OaaS (Outcomes-as-a-Service) business model: **No Uplift = No Fee**.

## Core Functionality

### 1. Settlement Calculation
Calculate performance-based fees based on revenue uplift:
- Compare actual revenue vs. baseline
- Apply 20% success fee only on positive uplift
- Zero fee if no uplift detected

### 2. QBR Report Generation
Generate professional PDF Quarterly Business Review reports:
- Financial summary with settlement details
- Performance metrics integration (from SyncValue)
- Automated retention (90 days)

## Quick Start

### 1. Install Dependencies
```bash
cd /workspaces/kiki-agent-syncshield/services/syncbill
pip install -r requirements.txt
```

### 2. Run the Service
```bash
python app/main.py
# Service runs on http://localhost:8008
```

### 3. Test the Service
```bash
# Run all tests
pytest tests/test_syncbill.py -v

# Expected: 22 tests passing
```

### 4. Try Examples
```bash
python example_syncbill.py
```

## API Examples

### Calculate Settlement (Positive Uplift)
```bash
curl -X POST http://localhost:8008/api/v1/settlement/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "client_acme",
    "billing_cycle": "Q1 2026",
    "total_revenue": 150000.0,
    "baseline_revenue": 100000.0
  }'

# Response:
# {
#   "settlement_id": "settlement_xyz789",
#   "attributed_uplift": 50000.0,
#   "kiki_success_fee": 10000.0,      ← 20% of $50k uplift
#   "client_net_benefit": 40000.0,    ← Client keeps $40k
#   "status": "SETTLEMENT_CALCULATED"
# }
```

### Calculate Settlement (No Uplift)
```bash
curl -X POST http://localhost:8008/api/v1/settlement/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "client_beta",
    "billing_cycle": "Q1 2026",
    "total_revenue": 95000.0,
    "baseline_revenue": 100000.0
  }'

# Response:
# {
#   "settlement_id": "settlement_abc456",
#   "attributed_uplift": -5000.0,
#   "kiki_success_fee": 0.0,           ← No uplift = No fee
#   "client_net_benefit": 0.0,
#   "status": "NO_UPLIFT_DETECTED"
# }
```

### Generate QBR Report
```bash
curl -X POST http://localhost:8008/api/v1/qbr/generate \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Acme Corp",
    "client_id": "client_acme",
    "period": "Q1 2026",
    "include_metrics": true
  }'

# Response:
# {
#   "report_id": "qbr_abc123",
#   "file_path": "/tmp/kiki_reports/qbr_client_acme_Q1_2026_abc123.pdf",
#   "download_url": "/api/v1/reports/qbr_abc123/download",
#   "expires_at": "2026-04-15T11:00:00Z"
# }
```

### Download Report
```bash
curl http://localhost:8008/api/v1/reports/qbr_abc123/download \
  -o report.pdf
```

## Settlement Calculation Examples

### Example 1: Strong Performance
```
Total Revenue:    $250,000
Baseline Revenue: $180,000
─────────────────────────────
Uplift:           $ 70,000
KIKI Fee (20%):   $ 14,000
Client Benefit:   $ 56,000  ← Client gets 80% of uplift
```

### Example 2: Moderate Performance
```
Total Revenue:    $120,000
Baseline Revenue: $100,000
─────────────────────────────
Uplift:           $ 20,000
KIKI Fee (20%):   $  4,000
Client Benefit:   $ 16,000
```

### Example 3: No Growth
```
Total Revenue:    $ 90,000
Baseline Revenue: $100,000
─────────────────────────────
Uplift:           $-10,000
KIKI Fee:         $      0  ← No uplift = No fee
Client Benefit:   $      0
```

## Health Check
```bash
curl http://localhost:8008/health

# Response:
# {
#   "status": "healthy",
#   "service": "syncbill",
#   "version": "1.0.0",
#   "metrics": {
#     "settlements_processed": 42,
#     "qbr_reports_generated": 18
#   }
# }
```

## Monitoring

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

## Configuration

Environment variables:
```bash
export SUCCESS_FEE_RATE=0.20          # 20% success fee
export MINIMUM_UPLIFT_THRESHOLD=0.0   # No fee if uplift ≤ 0
export REPORTS_DIR=/tmp/kiki_reports
export REPORT_RETENTION_DAYS=90
export SYNCVALUE_URL=http://syncvalue:8002
export SYNCSHIELD_URL=http://syncshield:8006
```

## Docker Deployment

### Build Image
```bash
docker build -t syncbill:latest -f services/syncbill/Dockerfile .
```

### Run Container
```bash
docker run -p 8008:8008 \
  -e SYNCVALUE_URL=http://syncvalue:8002 \
  -e SYNCSHIELD_URL=http://syncshield:8006 \
  syncbill:latest
```

### docker-compose
```bash
docker-compose up syncbill
```

## File Structure

```
services/syncbill/
├── app/
│   └── main.py               # Main FastAPI application (650 lines)
├── tests/
│   └── test_syncbill.py      # Test suite (22 tests)
├── Dockerfile                 # Production container
├── requirements.txt           # Python dependencies
├── README.md                  # Full documentation
├── QUICKSTART.md              # This file
├── IMPLEMENTATION_SUMMARY.md  # Technical details
└── example_syncbill.py        # Usage examples
```

## Integration with Other Services

### SyncValue (port 8002)
- Fetches performance metrics
- Provides revenue attribution data

### SyncShield (port 8006)
- Logs settlements for compliance
- Maintains audit trail

### API Gateway
- Routes external billing requests
- Handles authentication

## Troubleshooting

### Issue: Service won't start
**Solution**: Ensure all dependencies installed: `pip install -r requirements.txt`

### Issue: QBR generation fails
**Solution**: Ensure reports directory writable: `mkdir -p /tmp/kiki_reports`

### Issue: Tests fail
**Solution**: Run from workspace root: `cd /workspaces/kiki-agent-syncshield && pytest services/syncbill/tests/ -v`

## Next Steps

1. **View Full Documentation**: See [README.md](README.md)
2. **Run Examples**: `python example_syncbill.py`
3. **Deploy with Docker**: `docker-compose up syncbill`
4. **Monitor with Prometheus**: `curl http://localhost:8008/metrics`

## Key Features

✅ **Performance-Based Pricing**: No uplift = No fee  
✅ **Transparent Reporting**: Full financial breakdown  
✅ **Professional QBR Reports**: Automated PDF generation  
✅ **Service Integration**: SyncValue + SyncShield  
✅ **Enterprise Monitoring**: Prometheus + OpenTelemetry  
✅ **Comprehensive Testing**: 22 tests, 100% passing  
✅ **Production Ready**: Docker + Health checks

---

**Status**: ✅ Implemented and tested  
**Tests**: 22/22 passing  
**Documentation**: Complete  
**Deployment**: Ready
