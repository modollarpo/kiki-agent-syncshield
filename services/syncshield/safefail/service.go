package safefail

import (
	"context"
	"log"
	"net"
	"net/http"

	sfpb "kiki-agent-syncshield/safefail/github.com/kiki-agent/services/syncshield/safefail"

	"google.golang.org/grpc"
)

// SafeFailServer implements the gRPC SafeFailService
type SafeFailServer struct {
	sfpb.UnimplementedSafeFailServiceServer
	Guard *SafeFailGuard
}

func (s *SafeFailServer) TriggerRollback(ctx context.Context, req *sfpb.RollbackRequest) (*sfpb.RollbackResponse, error) {
	err := s.Guard.RollbackFunc(req.Reason)
	if err != nil {
		return &sfpb.RollbackResponse{Success: false, Message: err.Error()}, nil
	}
	return &sfpb.RollbackResponse{Success: true, Message: "Rollback triggered"}, nil
}

func (s *SafeFailServer) GetStatus(ctx context.Context, req *sfpb.StatusRequest) (*sfpb.StatusResponse, error) {
	return &sfpb.StatusResponse{
		LastScore:     s.Guard.lastScore,
		ThresholdDrop: s.Guard.ThresholdDrop,
		ThresholdNeg:  int32(s.Guard.ThresholdNeg),
		Status:        "OK",
	}, nil
}

func StartRESTAndGRPC(guard *SafeFailGuard) {
	// REST
	go func() {
		log.Println("[SafeFail] REST API on :8080")
		http.Handle("/safefail", guard)
		http.ListenAndServe(":8080", nil)
	}()
	// gRPC
	go func() {
		log.Println("[SafeFail] gRPC API on :50057")
		lis, err := net.Listen("tcp", ":50057")
		if err != nil {
			log.Fatalf("failed to listen: %v", err)
		}
		grpcServer := grpc.NewServer()
		sfpb.RegisterSafeFailServiceServer(grpcServer, &SafeFailServer{Guard: guard})
		if err := grpcServer.Serve(lis); err != nil {
			log.Fatalf("failed to serve: %v", err)
		}
	}()
}
