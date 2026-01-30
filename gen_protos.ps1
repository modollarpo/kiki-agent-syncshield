# Proto Generation Automation for KIKI Agent
# Usage: pwsh ./gen_protos.ps1

# Generate protos in shared/proto
Write-Output "Generating protos in shared/proto..."
Push-Location "${PSScriptRoot}\shared\proto"
Get-ChildItem *.proto | ForEach-Object { protoc --proto_path=. --go_out=gen --go-grpc_out=gen $_.Name }
Pop-Location

Write-Output "Generating protos in services/syncshield/safefail..."
Push-Location "${PSScriptRoot}\services\syncshield\safefail"
protoc --proto_path=. --go_out=. --go-grpc_out=. safefail.proto
Pop-Location

Write-Output "Generating protos in schemas..."
Push-Location "${PSScriptRoot}\schemas"
protoc --proto_path=. --go_out=. --go-grpc_out=. explainability_notification.proto
Pop-Location

Write-Output "Proto generation complete."
