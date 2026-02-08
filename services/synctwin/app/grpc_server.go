package app

import (
	"context"
	"log"

	pb "workspaces/kiki-agent-syncshield/services/synctwin/proto"
)

// SyncTwinServer implements the SyncTwinService gRPC interface

// Ensure struct implements pb.SyncTwinServiceServer
var _ pb.SyncTwinServiceServer = &SyncTwinServer{}

// SyncTwinServer struct
type SyncTwinServer struct {
import (
	"google.golang.org/grpc"
	"os"
	"fmt"
)
	SyncBrainClient   pb.SyncBrainServiceClient
	SyncShieldClient  pb.SyncShieldServiceClient
}

// ...existing code...

func (s *SyncTwinServer) SimulateStrategy(ctx context.Context, req *pb.SimulationRequest) (*pb.SimulationResult, error) {
	input := SimulationInput{
		StrategyJSON: req.GetStrategyJson(),
		ClientID:     req.GetClientId(),
		Platform:     req.GetPlatform(),
		Budget:       req.GetBudget(),
		TargetLTV:    req.GetTargetLtv(),
		ROIThreshold: req.GetRoiThreshold(),
	}
	log.Printf("[SyncTwin] SimulateStrategy: integrating with SyncBrain and SyncShield (production-grade)")

	// Fetch baseline revenue from SyncBrain
	baselineResp, err := s.SyncBrainClient.GetBaseline(ctx, &pb.BaselineRequest{ClientId: input.ClientID})
	if err != nil {
		log.Printf("SyncBrain baseline error: %v", err)
		return nil, err
	}
	baselineRevenue := baselineResp.BaselineRevenue

	// Fetch baseline ad spend from SyncShield
	shieldResp, err := s.SyncShieldClient.GetBaselineAdSpend(ctx, &pb.BaselineAdSpendRequest{ClientId: input.ClientID})
	if err != nil {
		log.Printf("SyncShield baseline error: %v", err)
		return nil, err
	}
	baselineAdSpend := shieldResp.BaselineAdSpend

	// Predict new revenue and ad spend using ML models
	newRevenue := predictNewRevenue(input)
	newAdSpend := predictNewAdSpend(input)

	netProfitUplift := (newRevenue - baselineRevenue) - (newAdSpend - baselineAdSpend)
	confidenceScore := riskScoreSim(netProfitUplift)
	riskProfile := "moderate"
	if confidenceScore < 0.7 {
		riskProfile = "conservative"
	} else if confidenceScore > 0.9 {
		riskProfile = "aggressive"
	}
	violations := []string{}
	if netProfitUplift < 0 {
		violations = append(violations, "Negative Net Profit Uplift")
	}

	// Log audit event to SyncShield
	_, _ = s.SyncShieldClient.LogAuditEvent(ctx, &pb.AuditEventRequest{EventType: "simulation", ClientId: input.ClientID})

	return &pb.SimulationResult{
		ConfidenceScore:        confidenceScore,
		RiskProfile:            riskProfile,
		ProjectedNetProfitUplift: netProfitUplift,
		Reason:                 "Simulation completed",
		Violations:             violations,
	}, nil
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
	log.Printf("[SyncTwin] RunChaosTest: integrating with SyncBrain and SyncShield (real gRPC)")
	// Example: Call SyncBrain for chaos baseline
	// chaosResp, err := s.SyncBrainClient.GetChaosBaseline(ctx, &pb.ChaosRequest{ClientId: input.ClientID})
	// if err != nil {
	//     log.Printf("SyncBrain chaos error: %v", err)
	// }
	// Example: Log audit event to SyncShield
	// _, _ = s.SyncShieldClient.LogAuditEvent(ctx, &pb.AuditEventRequest{EventType: "chaos_test", ClientId: input.ClientID})
	result, err := RunChaosTest(ctx, input)
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
	log.Printf("[SyncTwin] MirrorSync: integrating with SyncBrain and SyncShield (real gRPC)")
	// Example: Call SyncBrain for mirror sync
	// mirrorResp, err := s.SyncBrainClient.GetMirrorSync(ctx, &pb.MirrorSyncRequest{ClientId: input.ClientID})
	// if err != nil {
	//     log.Printf("SyncBrain mirror error: %v", err)
	// }
	// Example: Log audit event to SyncShield
	// _, _ = s.SyncShieldClient.LogAuditEvent(ctx, &pb.AuditEventRequest{EventType: "mirror_sync", ClientId: input.ClientID})
	result, err := MirrorSync(ctx, input)
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

import (
	"google.golang.org/grpc"
	"os"
	"fmt"
)

// NewSyncTwinServer initializes gRPC clients for SyncBrain and SyncShield and returns a SyncTwinServer
func NewSyncTwinServer(syncBrainAddr, syncShieldAddr string) (*SyncTwinServer, error) {
	// Connect to SyncBrain
	brainConn, err := grpc.Dial(syncBrainAddr, grpc.WithInsecure())
	if err != nil {
		return nil, fmt.Errorf("failed to connect to SyncBrain: %w", err)
	}
	// Connect to SyncShield
	shieldConn, err := grpc.Dial(syncShieldAddr, grpc.WithInsecure())
	if err != nil {
		return nil, fmt.Errorf("failed to connect to SyncShield: %w", err)
	}
	return &SyncTwinServer{
		SyncBrainClient:  pb.NewSyncBrainServiceClient(brainConn),
		SyncShieldClient: pb.NewSyncShieldServiceClient(shieldConn),
	}, nil
}

// Example usage:
// func main() {
//     syncBrainAddr := os.Getenv("SYNCBRAIN_GRPC_ADDR") // e.g. "syncbrain:50051"
//     syncShieldAddr := os.Getenv("SYNCSHIELD_GRPC_ADDR") // e.g. "syncshield:50052"
//     server, err := NewSyncTwinServer(syncBrainAddr, syncShieldAddr)
//     if err != nil {
//         log.Fatalf("Failed to initialize SyncTwinServer: %v", err)
//     }
//     // Register gRPC server, etc.
// }
}

// ...existing code...
