# SyncLedger™ Makefile - Build automation for OaaS Auditor

.PHONY: help build run test proto docker clean

# Default target
help:
	@echo "SyncLedger™ - Automated OaaS Auditor"
	@echo ""
	@echo "Available targets:"
	@echo "  make build       - Build the Go binary"
	@echo "  make run         - Run the service locally"
	@echo "  make test        - Run unit tests"
	@echo "  make proto       - Generate gRPC code from protobuf"
	@echo "  make docker      - Build Docker image"
	@echo "  make clean       - Remove build artifacts"
	@echo "  make lint        - Run code linters"
	@echo "  make migrate     - Run database migrations"

# Build the binary
build:
	@echo "🔨 Building SyncLedger™..."
	go build -o bin/syncledger main.go
	@echo "✅ Build complete: bin/syncledger"

# Run locally (requires PostgreSQL running)
run:
	@echo "🚀 Starting SyncLedger™..."
	@echo "gRPC: localhost:50053"
	@echo "HTTP: localhost:8090"
	go run main.go

# Run tests with coverage
test:
	@echo "🧪 Running tests..."
	go test -v -race -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html
	@echo "✅ Coverage report: coverage.html"

# Generate protobuf/gRPC code
proto:
	@echo "🔧 Generating gRPC code from protobuf..."
	mkdir -p proto
	protoc --go_out=proto --go_opt=paths=source_relative \
		--go-grpc_out=proto --go-grpc_opt=paths=source_relative \
		../../schemas/cms_integration.proto
	@echo "✅ Protobuf files generated in proto/"

# Build Docker image
docker:
	@echo "🐳 Building Docker image..."
	docker build -t kiki/syncledger:latest .
	@echo "✅ Image: kiki/syncledger:latest"

# Run Docker container
docker-run:
	@echo "🚀 Running SyncLedger™ in Docker..."
	docker run -d \
		--name syncledger \
		-p 50053:50053 \
		-p 8090:8090 \
		-e DATABASE_URL=postgres://kiki:password@host.docker.internal:5432/kiki_ledger \
		kiki/syncledger:latest

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -f bin/syncledger
	rm -f coverage.out coverage.html
	rm -rf proto/
	@echo "✅ Clean complete"

# Run code linters
lint:
	@echo "🔍 Running linters..."
	golangci-lint run
	@echo "✅ Lint complete"

# Database migrations (requires golang-migrate)
migrate:
	@echo "🗄️  Running database migrations..."
	migrate -path db/migrations -database "${DATABASE_URL}" up
	@echo "✅ Migrations complete"

# Download dependencies
deps:
	@echo "📦 Downloading dependencies..."
	go mod download
	go mod tidy
	@echo "✅ Dependencies updated"

# Run service with live reload (requires air)
dev:
	@echo "🔥 Starting development server with hot reload..."
	air

# gRPC testing with grpcurl
grpc-test:
	@echo "🧪 Testing gRPC endpoints..."
	grpcurl -plaintext localhost:50053 list
	grpcurl -plaintext localhost:50053 grpc.health.v1.Health/Check

# Health check
health:
	@echo "💚 Checking service health..."
	curl -s http://localhost:8090/healthz | jq .

# Prometheus metrics
metrics:
	@echo "📊 Fetching Prometheus metrics..."
	curl -s http://localhost:8090/metrics | grep syncledger

# Format code
fmt:
	@echo "✨ Formatting code..."
	go fmt ./...
	@echo "✅ Format complete"

# Run all CI checks (lint, test, build)
ci: lint test build
	@echo "✅ All CI checks passed"
