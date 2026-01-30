test:
	go test ./...
build:
	# Go gRPC codegen
	@mkdir -p internal/bidding_servicepb
	protoc --proto_path=../../shared/proto --go_out=internal/bidding_servicepb --go-grpc_out=internal/bidding_servicepb ../../shared/proto/bidding_service.proto
run:
	go run app/main.go
