# Proto Generation Automation for KIKI Agent (Bash)
# Usage: bash gen_protos.sh

set -e

# Generate protos in shared/proto
echo "Generating protos in shared/proto..."
cd "$(dirname "$0")/shared/proto"
for f in *.proto; do
  protoc --proto_path=. --go_out=gen --go-grpc_out=gen "$f"
done
cd - > /dev/null

# Generate protos in services/syncshield/safefail
echo "Generating protos in services/syncshield/safefail..."
cd "$(dirname "$0")/services/syncshield/safefail"
protoc --proto_path=. --go_out=. --go-grpc_out=. safefail.proto
cd - > /dev/null

# Generate protos in schemas
echo "Generating protos in schemas..."
cd "$(dirname "$0")/schemas"
protoc --proto_path=. --go_out=. --go-grpc_out=. explainability_notification.proto
cd - > /dev/null

echo "Proto generation complete."
