test:
	pytest
build:
	# Python gRPC codegen (example, update proto as needed)
	@mkdir -p app/grpc
	python -m grpc_tools.protoc -I=../../shared/proto --python_out=./app/grpc --grpc_python_out=./app/grpc ../../shared/proto/ltv_service.proto
run:
	uvicorn app.main:app --reload
