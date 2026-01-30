# Python gRPC Types

This folder contains Python code generated from proto contracts.

To generate Python gRPC stubs for kiki_core.proto, run:

```
python -m grpc_tools.protoc \
	-I../../proto \
	--python_out=. \
	--grpc_python_out=. \
	../../proto/kiki_core.proto
```

This will create kiki_core_pb2.py and kiki_core_pb2_grpc.py in this folder.
