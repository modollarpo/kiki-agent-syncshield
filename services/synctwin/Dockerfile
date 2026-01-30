FROM bitnami/golang:1.20
WORKDIR /app
COPY . /app
RUN go mod init synctwin && go mod tidy
CMD ["go", "run", "main.go"]
