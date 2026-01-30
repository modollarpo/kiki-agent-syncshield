# SyncShield Dockerfile
FROM golang:1.21-alpine as builder
WORKDIR /app
COPY ./app /app
RUN go mod init kiki-agent-syncshield || true
RUN go get github.com/gin-gonic/gin@v1.9.1
RUN go build -o syncshield main.go

FROM alpine:3.18
WORKDIR /app
COPY --from=builder /app/syncshield /app/syncshield
EXPOSE 8000
CMD ["/app/syncshield"]
