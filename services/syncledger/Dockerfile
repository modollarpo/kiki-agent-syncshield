# SyncLedger™ - Automated OaaS Auditor Dockerfile
FROM golang:1.24-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git make

WORKDIR /app

# Copy go.mod and go.sum first for better caching
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the binary with optimizations
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags='-w -s -extldflags "-static"' \
    -a -installsuffix cgo \
    -o syncledger \
    main.go

# Production image
FROM alpine:latest

# Install CA certificates for HTTPS connections and timezone data
RUN apk --no-cache add ca-certificates tzdata

# Create non-root user for security
RUN addgroup -S kiki && adduser -S kiki -G kiki

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/syncledger .

# Change ownership
RUN chown -R kiki:kiki /app

# Switch to non-root user
USER kiki

# Expose gRPC and HTTP ports
EXPOSE 50053 8090

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8090/healthz || exit 1

# Run the service
CMD ["./syncledger"]
