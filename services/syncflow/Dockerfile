# SyncFlow Dockerfile
FROM golang:1.24-alpine as builder
WORKDIR /build

# Copy go module files first for better caching
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the binary
RUN CGO_ENABLED=0 GOOS=linux go build -v -o syncflow .

FROM alpine:3.18
WORKDIR /app
COPY --from=builder /build/syncflow /app/syncflow
RUN chmod +x /app/syncflow
EXPOSE 8000
CMD ["/app/syncflow"]
