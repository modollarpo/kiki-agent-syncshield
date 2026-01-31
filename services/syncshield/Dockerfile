# SyncShield Dockerfile

FROM golang:1.21-alpine as builder
WORKDIR /app
# Copy go.mod and go.sum first for better cache usage
COPY ./app/go.mod ./app/go.sum ./
RUN go mod download
# Now copy the rest of the source
COPY ./app ./
RUN go build -o syncshield main.go

FROM alpine:3.18
WORKDIR /app
COPY --from=builder /app/syncshield /app/syncshield
EXPOSE 8000
CMD ["/app/syncshield"]
