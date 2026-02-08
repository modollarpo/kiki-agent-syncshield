package safefail

import (
	"context"
	"log"
	"time"
)

// SafeFailGuard monitors SyncReflex feedback and triggers rollbacks if needed.
type SafeFailGuard struct {
	ReflexEndpoint string
	RollbackFunc   func(reason string) error
	ThresholdDrop  float64 // e.g., -0.15 for 15% drop
	ThresholdNeg   int     // e.g., 10 negative events
	lastScore      float64
}

// Monitor runs the feedback loop in the background.
func (s *SafeFailGuard) Monitor(ctx context.Context) {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			s.checkReflex()
		}
	}
}

// checkReflex polls SyncReflex for feedback and triggers rollback if needed.
func (s *SafeFailGuard) checkReflex() {
	// Production: Poll SyncReflex via gRPC for feedback
	feedback, err := s.getReflexFeedback()
	if err != nil {
		log.Printf("[SafeFail] SyncReflex feedback error: %v", err)
		return
	}
	if feedback.PerformanceDrop <= s.ThresholdDrop || feedback.NegativeEvents >= s.ThresholdNeg {
		err := s.RollbackFunc("Auto Safe-Fail: performance or sentiment threshold breached")
		if err != nil {
			log.Printf("[SafeFail] Rollback failed: %v", err)
		} else {
			log.Printf("[SafeFail] Rollback triggered: %v", feedback)
		}
	}
}

type ReflexFeedback struct {
	PerformanceDrop float64 // e.g., -0.2 for 20% drop
	NegativeEvents  int
}

// getReflexFeedback polls SyncReflex via gRPC and returns feedback.
func (s *SafeFailGuard) getReflexFeedback() (ReflexFeedback, error) {
	// Example: Replace with real gRPC client call
	// client := NewSyncReflexClient(s.ReflexEndpoint)
	// resp, err := client.GetFeedback(context.Background())
	// if err != nil {
	//     return ReflexFeedback{}, err
	// }
	// return ReflexFeedback{
	//     PerformanceDrop: resp.PerformanceDrop,
	//     NegativeEvents:  resp.NegativeEvents,
	// }, nil

	// Temporary: Simulate feedback until proto is available
	return ReflexFeedback{PerformanceDrop: -0.18, NegativeEvents: 12}, nil
}
