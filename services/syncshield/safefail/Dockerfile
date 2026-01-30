FROM golang:1.21-alpine as builder
WORKDIR /app
COPY . .
RUN cd safefail && go build -o /app/safefail main.go

FROM alpine:3.18
WORKDIR /app
COPY --from=builder /app/safefail /app/safefail
COPY safefail/audit.log /app/audit.log
EXPOSE 8080 50057
CMD ["/app/safefail"]
