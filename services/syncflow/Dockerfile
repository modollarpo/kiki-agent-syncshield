# SyncFlow Dockerfile
FROM golang:1.24-alpine as builder
WORKDIR /app
COPY ./app /app
RUN go mod init kiki-agent-syncflow || true
RUN go get github.com/gin-gonic/gin@v1.9.1
RUN go get github.com/prometheus/client_golang/prometheus
RUN go get github.com/prometheus/client_golang/prometheus/promhttp
RUN go get go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin
RUN go get go.opentelemetry.io/otel
RUN go build -o syncflow main.go

FROM alpine:3.18
WORKDIR /app
COPY --from=builder /app/syncflow /app/syncflow
RUN chmod +x /app/syncflow
EXPOSE 8000
CMD ["/app/syncflow"]
