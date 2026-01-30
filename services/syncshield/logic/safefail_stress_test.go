package logic

import "testing"

func TestSafeFailRollback_Stress(t *testing.T) {
	manager := RollbackManager{MaxDriftThreshold: 0.20, StableAssetID: "gold_ad_123"}
	cases := []struct {
		current, baseline float64
		shouldRollback    bool
	}{
		{0.75, 1.0, true},  // >20% drop
		{0.80, 1.0, false}, // exactly 20% drop
		{0.79, 1.0, true},  // just over threshold
		{0.95, 1.0, false}, // healthy
		{0.0, 1.0, true},   // catastrophic
	}
	for i, c := range cases {
		result := manager.ValidatePerformance(c.current, c.baseline)
		if result == c.shouldRollback {
			t.Errorf("Case %d: expected rollback=%v, got %v", i, c.shouldRollback, result)
		}
	}
}
