# SafeFail Proto/gRPC Codegen & CI/CD Integration

## 1. Proto/gRPC Code Generation (Go)

Assuming you have `protoc` and `protoc-gen-go`/`protoc-gen-go-grpc` installed:

```bash
# From the root of your repo
protoc \
  --go_out=services/syncshield/safefail/proto \
  --go-grpc_out=services/syncshield/safefail/proto \
  services/syncshield/safefail/safefail.proto
```

- This will generate Go code in `services/syncshield/safefail/proto`.
- Update your Go imports to use `proto` package as needed.

## 2. CI/CD Automation (GitHub Actions)

Add this to `.github/workflows/syncshield-safefail.yml`:

```yaml
name: Build & Push SyncShield SafeFail
on:
  push:
    paths:
      - 'services/syncshield/safefail/**'
      - '.github/workflows/syncshield-safefail.yml'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.21'
      - name: Build
        run: |
          cd services/syncshield/safefail
          go build -o safefail main.go
      - name: Build Docker image
        run: |
          docker build -t syncshield-safefail:latest .
      - name: Push to Registry (optional)
        run: |
          echo "Add your docker login & push commands here"
```

## 3. Service Mesh Integration

- Expose gRPC (50057) and REST (8080) ports in your Kubernetes manifest (`service.yaml`).
- Register SafeFail with your mesh (e.g., Istio, Linkerd) for mTLS, discovery, and traffic policy.
- Add health/readiness probes to your deployment for mesh monitoring.

---

-**For further automation:**

- Add `protoc`/Go codegen as a pre-commit or CI step.
- Use mesh-specific annotations for traffic policy, circuit breaking, and observability.
- Integrate audit logs with your central logging/monitoring stack (e.g., Loki, ELK, Datadog).
