test:
	go test ./...
build:
	# Go gRPC codegen
	@mkdir -p internal/strategy_orchestratorpb
	protoc --proto_path=../../shared/proto --go_out=internal/strategy_orchestratorpb --go-grpc_out=internal/strategy_orchestratorpb ../../shared/proto/strategy_orchestrator.proto
run:
	go run app/main.go
