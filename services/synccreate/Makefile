test:
	pytest
build:
	# Python gRPC codegen (using bidding_service.proto as example)
	@mkdir -p app/grpc
	python -m grpc_tools.protoc -I=../../shared/proto --python_out=./app/grpc --grpc_python_out=./app/grpc ../../shared/proto/bidding_service.proto
run:
	uvicorn app.main:app --reload
