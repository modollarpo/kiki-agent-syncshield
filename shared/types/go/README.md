# Go gRPC Types

This folder contains Go code generated from proto contracts.

To generate/update:

```
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
protoc -I../../proto --go_out=. --go-grpc_out=. ../../proto/brain.proto ../../proto/value.proto ../../proto/shield.proto
```
