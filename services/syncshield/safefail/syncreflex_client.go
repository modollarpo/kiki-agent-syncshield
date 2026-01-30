package safefail

import (
	"time"

	"google.golang.org/grpc"
	// TODO: Add generated proto import for SyncReflex here when available
)

// SyncReflexClient wraps the gRPC client for SyncReflex feedback.
type SyncReflexClient struct {
	conn *grpc.ClientConn
	// client pb.SyncReflexServiceClient // Uncomment when proto is available
}

func NewSyncReflexClient(endpoint string) (*SyncReflexClient, error) {
	conn, err := grpc.Dial(endpoint, grpc.WithInsecure(), grpc.WithBlock(), grpc.WithTimeout(5*time.Second))
	if err != nil {
		return nil, err
	}
	// client := pb.NewSyncReflexServiceClient(conn) // Uncomment when proto is available
	return &SyncReflexClient{conn: conn}, nil
}

// func (c *SyncReflexClient) GetFeedback(ctx context.Context) (*pb.FeedbackResponse, error) {
//      // Replace with real request params as needed
//      return c.client.GetFeedback(ctx, &pb.FeedbackRequest{})
// }

func (c *SyncReflexClient) Close() {
	c.conn.Close()
}
