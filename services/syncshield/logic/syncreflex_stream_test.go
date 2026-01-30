package logic

import "testing"

func TestSyncReflexPerformanceDrop(t *testing.T) {
	baseline := 1.0
	current := 0.75 // 25% drop
	manager := RollbackManager{MaxDriftThreshold: 0.20, StableAssetID: "gold_ad_123"}
	if manager.ValidatePerformance(current, baseline) {
		t.Error("Should trigger rollback on >20% drop")
	}
	current = 0.85 // 15% drop
	if !manager.ValidatePerformance(current, baseline) {
		t.Error("Should not trigger rollback on <20% drop")
	}
}
