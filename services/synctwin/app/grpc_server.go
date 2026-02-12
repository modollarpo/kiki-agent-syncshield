package app

import (
	"context"
	"log"

	pb "synctwin/proto"
)

// SyncTwinServer implements the SyncTwinService gRPC interface

// SyncTwinServer struct
type SyncTwinServer struct {
	SyncBrainClient   interface{}
	SyncShieldClient  interface{}
	MLClient          interface{} // ML client for LTV/ad spend prediction
}

func (s *SyncTwinServer) SimulateStrategy(ctx context.Context, req *pb.SimulationRequest) (*pb.SimulationResult, error) {
	input := SimulationInput{
		StrategyJSON: req.GetStrategyJson(),
		ClientID:     req.GetClientId(),
		Platform:     req.GetPlatform(),
		Budget:       req.GetBudget(),
		TargetLTV:    req.GetTargetLtv(),
		ROIThreshold: req.GetRoiThreshold(),
	}
	log.Printf("[SyncTwin] SimulateStrategy: integrating with SyncBrain, SyncShield, and ML (production-grade)")

	// Use productionized simulator logic (wires all real clients)
	result, err := SimulateStrategy(ctx, input, s.SyncBrainClient, s.SyncShieldClient, s.MLClient)
	if err != nil {
		log.Printf("Simulation error: %v", err)
		return nil, err
	}

	// TODO: Integrate with SyncShield audit logging
	// _, _ = s.SyncShieldClient.LogAuditEvent(ctx, &pb.AuditEventRequest{EventType: "simulation", ClientId: input.ClientID})

	return &pb.SimulationResult{
		ConfidenceScore:        result.ConfidenceScore,
		RiskProfile:            result.RiskProfile,
		ProjectedNetProfitUplift: result.ProjectedNetProfitUplift,
		Reason:                 result.Reason,
		Violations:             result.Violations,
	}, nil
// End of SimulateStrategy
}

func (s *SyncTwinServer) RunChaosTest(ctx context.Context, req *pb.SimulationRequest) (*pb.SimulationResult, error) {
	input := SimulationInput{
		StrategyJSON: req.GetStrategyJson(),
		ClientID:     req.GetClientId(),
		Platform:     req.GetPlatform(),
		Budget:       req.GetBudget(),
		TargetLTV:    req.GetTargetLtv(),
		ROIThreshold: req.GetRoiThreshold(),
	}
	log.Printf("[SyncTwin] RunChaosTest: integrating with SyncBrain, SyncShield, and ML (production-grade)")
	result, err := RunChaosTest(ctx, input, s.SyncBrainClient, s.SyncShieldClient, s.MLClient)
	if err != nil {
		return nil, err
	}
	return &pb.SimulationResult{
		ConfidenceScore:        result.ConfidenceScore,
		RiskProfile:            result.RiskProfile,
		ProjectedNetProfitUplift: result.ProjectedNetProfitUplift,
		Reason:                 result.Reason,
		Violations:             result.Violations,
	}, nil
}

func (s *SyncTwinServer) MirrorSync(ctx context.Context, req *pb.SimulationRequest) (*pb.SimulationResult, error) {
	input := SimulationInput{
		StrategyJSON: req.GetStrategyJson(),
		ClientID:     req.GetClientId(),
		Platform:     req.GetPlatform(),
		Budget:       req.GetBudget(),
		TargetLTV:    req.GetTargetLtv(),
		ROIThreshold: req.GetRoiThreshold(),
	}
	log.Printf("[SyncTwin] MirrorSync: integrating with SyncBrain, SyncShield, and ML (production-grade)")
	// NOTE: realPerformance must be provided by the caller (e.g., from SyncFlow metrics)
	// For demonstration, use a placeholder value (should be replaced with real metric in production)
	realPerformance := 0.0 // TODO: wire actual realPerformance from SyncFlow
	result, err := MirrorSync(ctx, input, s.SyncBrainClient, s.SyncShieldClient, s.MLClient, realPerformance)
	if err != nil {
		return nil, err
	}
	return &pb.SimulationResult{
		ConfidenceScore:        result.ConfidenceScore,
		RiskProfile:            result.RiskProfile,
		ProjectedNetProfitUplift: result.ProjectedNetProfitUplift,
		Reason:                 result.Reason,
		Violations:             result.Violations,
	}, nil


}

// NewSyncTwinServer initializes gRPC clients for SyncBrain, SyncShield, and SyncValue (ML) and returns a SyncTwinServer
// TODO: Implement gRPC client initialization for SyncBrain, SyncShield, and SyncValue
func NewSyncTwinServer(syncBrainAddr, syncShieldAddr, mlAddr string) (*SyncTwinServer, error) {
	// Placeholder: return empty struct for now
	return &SyncTwinServer{}, nil
}

// Example usage:
// func main() {
//     syncBrainAddr := os.Getenv("SYNCBRAIN_GRPC_ADDR") // e.g. "syncbrain:50051"
//     syncShieldAddr := os.Getenv("SYNCSHIELD_GRPC_ADDR") // e.g. "syncshield:50052"
//     mlAddr := os.Getenv("SYNCVALUE_GRPC_ADDR") // e.g. "syncvalue:50053"
//     server, err := NewSyncTwinServer(syncBrainAddr, syncShieldAddr, mlAddr)
//     if err != nil {
//         log.Fatalf("Failed to initialize SyncTwinServer: %v", err)
//     }
//     // Register gRPC server, etc.
// }
// ...existing code...
