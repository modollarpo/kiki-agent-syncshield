FROM golang:1.22-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o /out/synctwin ./

FROM alpine:3.20
WORKDIR /app
COPY --from=build /out/synctwin /usr/local/bin/synctwin
EXPOSE 8000
ENV PORT=8000
CMD ["/usr/local/bin/synctwin"]
