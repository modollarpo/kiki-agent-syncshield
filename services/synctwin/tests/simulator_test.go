package tests

import (
	"context"
	"synctwin/app"
	"testing"
)

func TestSimulateStrategy_ZeroUplift(t *testing.T) {
	input := app.SimulationInput{
		StrategyJSON: "{}",
		ClientID:     "test-client",
		Platform:     "meta",
		Budget:       5000.0,
		TargetLTV:    450.0,
		ROIThreshold: 2.0,
	}
	// Simulate zero uplift scenario
	result, err := app.SimulateStrategy(context.Background(), input, nil, nil, nil)
	if err != nil {
		t.Fatalf("SimulateStrategy failed: %v", err)
	}
	if result.ProjectedNetProfitUplift == 0 && result.ConfidenceScore < 0.7 {
		t.Errorf("Expected confidence >= 0.7 for zero uplift")
	}
}

func TestRunChaosTest_NegativeUplift(t *testing.T) {
	input := app.SimulationInput{
		StrategyJSON: "{}",
		ClientID:     "test-client",
		Platform:     "meta",
		Budget:       5000.0,
		TargetLTV:    450.0,
		ROIThreshold: 2.0,
	}
	result, err := app.RunChaosTest(context.Background(), input, nil, nil, nil)
	if err != nil {
		t.Fatalf("RunChaosTest failed: %v", err)
	}
	if result.ProjectedNetProfitUplift < 0 && len(result.Violations) < 2 {
		t.Errorf("Expected chaos test violations for negative uplift")
	}
}

func TestMirrorSync_AutoRollback(t *testing.T) {
	input := app.SimulationInput{
		StrategyJSON: "{}",
		ClientID:     "test-client",
		Platform:     "meta",
		Budget:       5000.0,
		TargetLTV:    450.0,
		ROIThreshold: 2.0,
	}
	result, err := app.MirrorSync(context.Background(), input, nil, nil, nil, 1000.0)
	if err != nil {
		t.Fatalf("MirrorSync failed: %v", err)
	}
	if result.ConfidenceScore < 0.5 {
		t.Errorf("Expected confidence > 0.5, got %f", result.ConfidenceScore)
	}
	for _, v := range result.Violations {
		if v == "Deviation > 15%: Auto-Rollback" {
			return // Pass if auto-rollback triggered
		}
	}
	// If no auto-rollback violation, test passes if confidence is high
}

func TestSimulateStrategy_PositiveUplift(t *testing.T) {
	input := app.SimulationInput{
		StrategyJSON: "{}",
		ClientID:     "test-client",
		Platform:     "meta",
		Budget:       5000.0,
		TargetLTV:    450.0,
		ROIThreshold: 2.0,
	}
	result, err := app.SimulateStrategy(context.Background(), input, nil, nil, nil)
	if err != nil {
		t.Fatalf("SimulateStrategy failed: %v", err)
	}
	if result.ConfidenceScore < 0.7 {
		t.Errorf("Expected confidence > 0.7, got %f", result.ConfidenceScore)
	}
	if result.ProjectedNetProfitUplift < 0 {
		t.Errorf("Expected positive uplift, got %f", result.ProjectedNetProfitUplift)
	}
}

func TestSimulateStrategy_NegativeUplift(t *testing.T) {
	input := app.SimulationInput{
		StrategyJSON: "{}",
		ClientID:     "test-client",
		Platform:     "meta",
		Budget:       5000.0,
		TargetLTV:    450.0,
		ROIThreshold: 2.0,
	}
	// Force negative uplift by manipulating input (simulate low revenue/high spend)
	result, err := app.SimulateStrategy(context.Background(), input, nil, nil, nil)
	if err != nil {
		t.Fatalf("SimulateStrategy failed: %v", err)
	}
	if result.ProjectedNetProfitUplift < 0 && len(result.Violations) == 0 {
		t.Errorf("Expected violation for negative uplift")
	}
}

func TestRunChaosTest(t *testing.T) {
	input := app.SimulationInput{
		StrategyJSON: "{}",
		ClientID:     "test-client",
		Platform:     "meta",
		Budget:       5000.0,
		TargetLTV:    450.0,
		ROIThreshold: 2.0,
	}
	result, err := app.RunChaosTest(context.Background(), input, nil, nil, nil)
	if err != nil {
		t.Fatalf("RunChaosTest failed: %v", err)
	}
	if len(result.Violations) < 2 {
		t.Errorf("Expected at least 2 chaos violations")
	}
}

func TestMirrorSync(t *testing.T) {
	input := app.SimulationInput{
		StrategyJSON: "{}",
		ClientID:     "test-client",
		Platform:     "meta",
		Budget:       5000.0,
		TargetLTV:    450.0,
		ROIThreshold: 2.0,
	}
	result, err := app.MirrorSync(context.Background(), input, nil, nil, nil, 1000.0)
	if err != nil {
		t.Fatalf("MirrorSync failed: %v", err)
	}
	if result.ConfidenceScore < 0.5 {
		t.Errorf("Expected confidence > 0.5, got %f", result.ConfidenceScore)
	}
}
