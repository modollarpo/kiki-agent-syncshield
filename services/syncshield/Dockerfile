# SyncShield Dockerfile

FROM golang:1.24-alpine as builder
WORKDIR /app

# Copy go.mod and go.sum from the service root for better cache usage
COPY go.mod go.sum ./
RUN go mod download

# Now copy the rest of the source
COPY . .

# Build the SyncShield service binary from the app entrypoint
RUN go build -o syncshield ./app

FROM alpine:3.18
WORKDIR /app
COPY --from=builder /app/syncshield /app/syncshield
EXPOSE 8000
CMD ["/app/syncshield"]
