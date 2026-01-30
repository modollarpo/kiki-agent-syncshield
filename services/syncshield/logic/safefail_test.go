package logic

import "testing"

func TestValidatePerformance(t *testing.T) {
	manager := RollbackManager{MaxDriftThreshold: 0.20, StableAssetID: "gold_ad_123"}
	if manager.ValidatePerformance(0.75, 1.0) {
		t.Error("Should trigger rollback when drift > threshold")
	}
	if !manager.ValidatePerformance(0.85, 1.0) {
		t.Error("Should not trigger rollback when drift <= threshold")
	}
}
