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
	// TODO: Replace with real HTTP/gRPC call to SyncReflex
	feedback := mockReflexFeedback()
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

func mockReflexFeedback() ReflexFeedback {
	// TODO: Replace with real data
	return ReflexFeedback{PerformanceDrop: -0.18, NegativeEvents: 12}
}
