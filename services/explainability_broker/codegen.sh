#!/bin/bash
# Generate Python and Go code from explainability_notification.proto
PROTO=../../schemas/explainability_notification.proto
OUT_PY=./gen_py
OUT_GO=./gen_go
mkdir -p $OUT_PY $OUT_GO
python -m grpc_tools.protoc -I../../schemas --python_out=$OUT_PY --grpc_python_out=$OUT_PY $PROTO
goproto=$(which protoc-gen-go)
if [ -n "$goproto" ]; then
  protoc -I../../schemas --go_out=$OUT_GO --go-grpc_out=$OUT_GO $PROTO
fi
