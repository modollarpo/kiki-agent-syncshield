# KIKI Agent™ gRPC Codegen & Developer Guide

## Automated gRPC Code Generation
Each service has a Makefile with a `build` target that automatically generates gRPC code for Go or Python from the shared proto contracts.

### Usage
- To generate gRPC code for a service, run:
  
  ```sh
  cd services/<service_name>
  make build
  ```
- This will:
  - For Go services: generate code into `internal/<proto>pb/`
  - For Python services: generate code into `app/grpc/`

### Example
- SyncValue (Python):
  ```sh
  cd services/syncvalue
  make build
  # Output: app/grpc/ltv_service_pb2.py, ltv_service_pb2_grpc.py
  ```
- SyncShield (Go):
  ```sh
  cd services/syncshield
  make build
  # Output: internal/strategy_orchestratorpb/strategy_orchestrator.pb.go, ...
  ```

## Adding New Proto Files
1. Place new proto files in `shared/proto/`.
2. Update the relevant service's Makefile to add a build step for the new proto.
3. Run `make build` in the service directory.

## Developer Notes
- Ensure you have `protoc`, `protoc-gen-go`, `protoc-gen-go-grpc`, and `grpcio-tools` installed.
- For Python, activate the correct virtual environment before running `make build`.
- For Go, ensure your `GOPATH` and Go tools are set up.
- Output directories are created automatically if missing.

## Troubleshooting
- If you see `No such file or directory`, ensure the output directory exists or rerun `make build`.
- If you add new proto files, always update the Makefile and re-run the build.

---
For more, see `/docs/ARCHITECTURE.md` and `/docs/API_REFERENCE.md`.
