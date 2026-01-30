# Shared

This folder contains all proto contracts and generated types for cross-service communication (gRPC, REST schemas).

- Place .proto files in subfolders by domain (e.g., brain.proto, value.proto, shield.proto).
- Generate language-specific types into /shared/types/{python,go}.# Shared Modules

- Common utilities, types, and constants for all services
- Place shared Python, Go, and Node.js code here
