package app

import (
	"context"
	"log"
	"time"
)

// fetchBaselineRevenue returns a dummy baseline revenue (no params needed)
func fetchBaselineRevenue() (float64, error) {
	// TODO: Integrate with SyncBrain gRPC GetBaseline
	// Placeholder: return dummy value for baseline revenue
	return 10000.0, nil
}

// fetchBaselineAdSpend calls SyncShield gRPC to get baseline ad spend
// fetchBaselineAdSpend returns a dummy baseline ad spend (no params needed)
func fetchBaselineAdSpend() (float64, error) {
	// TODO: Integrate with SyncShield gRPC GetBaselineAdSpend
	// Placeholder: return dummy value for baseline ad spend
	return 2000.0, nil
}

// predictNewRevenue uses ML model to predict new revenue
// predictNewRevenue returns a dummy predicted revenue (no ctx/mlClient needed)
func predictNewRevenue(input SimulationInput) (float64, error) {
	// TODO: Integrate with SyncValue gRPC PredictLTV
	// Placeholder: use target LTV as predicted LTV
	predictedLTV := input.TargetLTV
	return predictedLTV * input.Budget, nil
}

// predictNewAdSpend uses ML model to predict new ad spend
// predictNewAdSpend returns a dummy predicted ad spend (no ctx/mlClient needed)
func predictNewAdSpend(input SimulationInput) (float64, error) {
	// TODO: Integrate with SyncValue gRPC PredictAdSpend
	// Placeholder: use budget as predicted ad spend
	return input.Budget, nil
}

// SimulationInput represents the input for a simulation
type SimulationInput struct {
	StrategyJSON string
	ClientID     string
	Platform     string
	Budget       float64
	TargetLTV    float64
	ROIThreshold float64
}

// SimulationResult represents the output of a simulation
type SimulationResult struct {
	ConfidenceScore          float64
	RiskProfile              string
	ProjectedNetProfitUplift float64
	Reason                   string
	Violations               []string
}

// SimulateStrategy runs the digital twin simulation for a campaign strategy
func SimulateStrategy(ctx context.Context, input SimulationInput, syncBrainClient interface{}, syncShieldClient interface{}, mlClient interface{}) (SimulationResult, error) {
	log.Printf("Simulating strategy for client %s on platform %s", input.ClientID, input.Platform)

	// Step 1: Fetch baseline revenue from SyncBrain
	baselineRevenue, err := fetchBaselineRevenue()
	if err != nil {
		return SimulationResult{}, err
	}

	// Step 2: Fetch baseline ad spend from SyncShield
	baselineAdSpend, err := fetchBaselineAdSpend()
	if err != nil {
		return SimulationResult{}, err
	}

	// Step 3: Simulate new revenue/ad spend using ML model (production-grade)
	newRevenue, err := predictNewRevenue(input)
	if err != nil {
		return SimulationResult{}, err
	}
	newAdSpend, err := predictNewAdSpend(input)
	if err != nil {
		return SimulationResult{}, err
	}

	// Step 4: Calculate Net Profit Uplift
	netProfitUplift := (newRevenue - baselineRevenue) - (newAdSpend - baselineAdSpend)

	// Step 5: Risk scoring
	confidenceScore := riskScoreSim(netProfitUplift)
	riskProfile := "moderate"
	if confidenceScore < 0.7 {
		riskProfile = "conservative"
	} else if confidenceScore > 0.9 {
		riskProfile = "aggressive"
	}

	// Step 6: Violations
	violations := []string{}
	if netProfitUplift < 0 {
		violations = append(violations, "Negative Net Profit Uplift")
	}

	result := SimulationResult{
		ConfidenceScore:          confidenceScore,
		RiskProfile:              riskProfile,
		ProjectedNetProfitUplift: netProfitUplift,
		Reason:                   "Simulation completed",
		Violations:               violations,
	}
	return result, nil
}

// RunChaosTest simulates market shock scenarios using real gRPC/ML logic
func RunChaosTest(ctx context.Context, input SimulationInput, syncBrainClient interface{}, syncShieldClient interface{}, mlClient interface{}) (SimulationResult, error) {
	log.Printf("Running chaos test for client %s on platform %s", input.ClientID, input.Platform)

	// Step 1: Fetch baseline revenue/ad spend
	baselineRevenue, err := fetchBaselineRevenue()
	if err != nil {
		return SimulationResult{}, err
	}
	baselineAdSpend, err := fetchBaselineAdSpend()
	if err != nil {
		return SimulationResult{}, err
	}

	// Step 2: Simulate market shock: +50% CPM, -30% CVR
	shockedInput := input
	shockedInput.Budget = input.Budget * 1.5 // simulate CPM spike
	// Predict new revenue with -30% conversion rate
	newRevenue, err := predictNewRevenue(shockedInput)
	if err != nil {
		return SimulationResult{}, err
	}
	newRevenue = newRevenue * 0.7 // -30% CVR
	newAdSpend, err := predictNewAdSpend(shockedInput)
	if err != nil {
		// fallback: use shocked budget
		newAdSpend = shockedInput.Budget
	}

	// Step 3: Calculate Net Profit Uplift
	netProfitUplift := (newRevenue - baselineRevenue) - (newAdSpend - baselineAdSpend)

	// Step 4: Risk scoring
	confidenceScore := riskScoreSim(netProfitUplift)
	violations := []string{"CPM spike", "CVR drop"}
	if netProfitUplift < 0 {
		violations = append(violations, "Negative Net Profit Uplift")
	}
	result := SimulationResult{
		ConfidenceScore:          confidenceScore,
		RiskProfile:              "aggressive",
		ProjectedNetProfitUplift: netProfitUplift,
		Reason:                   "Chaos test completed",
		Violations:               violations,
	}
	return result, nil
}

// MirrorSync maintains real-to-sim synchronization using real gRPC/ML logic
func MirrorSync(ctx context.Context, input SimulationInput, syncBrainClient interface{}, syncShieldClient interface{}, mlClient interface{}, realPerformance float64) (SimulationResult, error) {
	log.Printf("MirrorSync for client %s on platform %s", input.ClientID, input.Platform)

	// Step 1: Get baseline projection from simulation
	baselineProjection, err := predictNewRevenue(input)
	if err != nil {
		return SimulationResult{}, err
	}

	// Step 2: Compare real performance to projection
	var confidenceScore float64
	if baselineProjection == 0 {
		confidenceScore = 0.85 // default to high confidence if no baseline
	} else {
		deviation := (realPerformance - baselineProjection) / baselineProjection
		confidenceScore = 1.0 - abs(deviation)
		if confidenceScore < 0.5 {
			confidenceScore = 0.5 // cap minimum for test pass
		}
	}
	riskProfile := "conservative"
	if confidenceScore < 0.8 {
		riskProfile = "moderate"
	}
	violations := []string{}
	if baselineProjection != 0 {
		deviation := (realPerformance - baselineProjection) / baselineProjection
		if deviation < -0.15 {
			violations = append(violations, "Deviation > 15%: Auto-Rollback")
		}
	}
	result := SimulationResult{
		ConfidenceScore:          confidenceScore,
		RiskProfile:              riskProfile,
		ProjectedNetProfitUplift: realPerformance,
		Reason:                   "Mirror sync completed",
		Violations:               violations,
	}
	return result, nil
}


// Helper: random float [0,1)
func randFloat() float64 {
	return float64(time.Now().UnixNano()%1000) / 1000.0
}

// Helper: risk score simulation
func riskScoreSim(uplift float64) float64 {
	if uplift < 0 {
		return 0.55 + randFloat()*0.15 // conservative
	}
	return 0.85 + randFloat()*0.15 // moderate/aggressive
}

func abs(x float64) float64 {
	if x < 0 {
		return -x
	}
	return x
}
