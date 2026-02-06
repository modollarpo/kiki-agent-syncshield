package internal

import (
	"encoding/json"
	"fmt"
	"math"
)

// UpliftCalculator handles all revenue attribution and success fee calculations
// Core OaaS Formula: SuccessFee = (CurrentRevenue - BaselineRevenue) * 0.20
type UpliftCalculator struct {
	// Configuration
	SuccessFeePercentage float64 // Default: 0.20 (20%)
	ConfidenceThreshold  float64 // Default: 0.70 (70% confidence required for attribution)
	NegativeUpliftPolicy string  // "zero_fee" or "carryforward"
}

// NewUpliftCalculator creates a calculator with default OaaS settings
func NewUpliftCalculator() *UpliftCalculator {
	return &UpliftCalculator{
		SuccessFeePercentage: 0.20,       // 20% success fee
		ConfidenceThreshold:  0.70,       // 70% attribution confidence threshold
		NegativeUpliftPolicy: "zero_fee", // No fee if uplift is negative
	}
}

// AttributionDecision represents the result of an attribution calculation
type AttributionDecision struct {
	// Input Data
	OrderAmount     float64
	BaselineRevenue float64
	Confidence      float64

	// Calculated Values
	IsAttributed       bool
	IncrementalRevenue float64
	UpliftPercentage   float64
	SuccessFee         float64
	FeeApplicable      bool

	// Attribution Breakdown
	Reason         string
	AgentsInvolved []string
	SignalScores   map[string]float64
	Counterfactual float64 // Estimated revenue without KIKI
}

// CalculateAttribution determines if an order should be attributed to KIKI
//
// Logic:
// 1. Check if attribution confidence >= threshold (default 0.70)
// 2. Calculate incremental revenue: OrderAmount - BaselineAvgOrderValue
// 3. If incremental > 0 AND confidence high: Attribute to KIKI
// 4. Calculate success fee: IncrementalRevenue * 0.20
//
// Edge Cases:
// - Negative uplift (order < baseline): Fee = $0
// - Low confidence (< 0.70): Not attributed, Fee = $0
// - First month (no baseline): Use store-level baseline average
func (u *UpliftCalculator) CalculateAttribution(
	orderAmount float64,
	baselineAvgOrderValue float64,
	confidence float64,
	signalScores map[string]float64,
) *AttributionDecision {
	decision := &AttributionDecision{
		OrderAmount:     orderAmount,
		BaselineRevenue: baselineAvgOrderValue,
		Confidence:      confidence,
		SignalScores:    signalScores,
		AgentsInvolved:  []string{},
	}

	// Step 1: Check confidence threshold
	if confidence < u.ConfidenceThreshold {
		decision.IsAttributed = false
		decision.FeeApplicable = false
		decision.Reason = fmt.Sprintf(
			"Attribution confidence %.2f below threshold %.2f",
			confidence, u.ConfidenceThreshold,
		)
		return decision
	}

	// Step 2: Calculate incremental revenue
	decision.IncrementalRevenue = orderAmount - baselineAvgOrderValue

	// Step 3: Check if uplift is positive
	if decision.IncrementalRevenue <= 0 {
		decision.IsAttributed = false
		decision.FeeApplicable = false
		decision.Reason = fmt.Sprintf(
			"Order value $%.2f below baseline $%.2f (negative uplift)",
			orderAmount, baselineAvgOrderValue,
		)
		return decision
	}

	// Step 4: Calculate uplift percentage
	if baselineAvgOrderValue > 0 {
		decision.UpliftPercentage = (decision.IncrementalRevenue / baselineAvgOrderValue) * 100
	}

	// Step 5: Attribution successful - calculate success fee
	decision.IsAttributed = true
	decision.FeeApplicable = true
	decision.SuccessFee = decision.IncrementalRevenue * u.SuccessFeePercentage

	// Step 6: Determine which agents contributed (based on signal scores)
	decision.AgentsInvolved = u.extractContributingAgents(signalScores)

	// Step 7: Generate human-readable explanation
	decision.Reason = u.generateExplanation(decision, signalScores)

	// Step 8: Calculate counterfactual (what revenue would have been without KIKI)
	decision.Counterfactual = baselineAvgOrderValue

	return decision
}

// CalculateMonthlyUplift computes the total uplift for a billing period
//
// Aggregates all attributed orders in a month:
// - Total Incremental Revenue = Sum(OrderAmount - Baseline) for all attributed orders
// - Success Fee = Total Incremental * 0.20
// - Uplift % = (ActualRevenue - BaselineRevenue) / BaselineRevenue * 100
func (u *UpliftCalculator) CalculateMonthlyUplift(
	baselineMonthlyRevenue float64,
	actualMonthlyRevenue float64,
	attributedOrdersRevenue float64,
	totalOrders int,
) *MonthlyUplift {
	uplift := &MonthlyUplift{
		BaselineRevenue: baselineMonthlyRevenue,
		ActualRevenue:   actualMonthlyRevenue,
		TotalOrders:     totalOrders,
	}

	// Calculate total incremental revenue
	uplift.IncrementalRevenue = actualMonthlyRevenue - baselineMonthlyRevenue

	// Check for negative uplift (KIKI underperformed)
	if uplift.IncrementalRevenue <= 0 {
		uplift.SuccessFee = 0.00
		uplift.FeeApplicable = false
		uplift.Reason = fmt.Sprintf(
			"Negative uplift: Actual $%.2f below Baseline $%.2f. Zero-Risk Policy: No fee charged.",
			actualMonthlyRevenue, baselineMonthlyRevenue,
		)
		return uplift
	}

	// Calculate uplift percentage
	if baselineMonthlyRevenue > 0 {
		uplift.UpliftPercentage = (uplift.IncrementalRevenue / baselineMonthlyRevenue) * 100
	}

	// Calculate success fee (20% of incremental)
	uplift.SuccessFee = uplift.IncrementalRevenue * u.SuccessFeePercentage
	uplift.FeeApplicable = true

	// Generate explanation
	uplift.Reason = fmt.Sprintf(
		"Revenue increased from $%.2f (baseline) to $%.2f (+%.1f%%). "+
			"KIKI generated $%.2f in incremental revenue. Success fee (20%%): $%.2f",
		baselineMonthlyRevenue, actualMonthlyRevenue, uplift.UpliftPercentage,
		uplift.IncrementalRevenue, uplift.SuccessFee,
	)

	return uplift
}

// MonthlyUplift represents aggregated performance for a billing period
type MonthlyUplift struct {
	BaselineRevenue    float64
	ActualRevenue      float64
	IncrementalRevenue float64
	UpliftPercentage   float64
	SuccessFee         float64
	FeeApplicable      bool
	TotalOrders        int
	Reason             string
}

// extractContributingAgents determines which KIKI agents influenced the sale
//
// Signal Scores (from attribution engine):
// - "ad_touchpoint": Customer clicked KIKI ad (SyncFlow)
// - "acquisition": Customer acquired via KIKI (SyncValue + SyncFlow)
// - "product_promotion": Product promoted by KIKI (SyncCreate)
// - "nurture_engagement": Customer engaged with SyncEngage flow
//
// Returns: ["SyncFlow", "SyncCreate", "SyncEngage"] based on >0.3 signal scores
func (u *UpliftCalculator) extractContributingAgents(signalScores map[string]float64) []string {
	agents := []string{}

	if signalScores["ad_touchpoint"] >= 0.3 {
		agents = append(agents, "SyncFlow") // Bidding & campaign management
	}

	if signalScores["acquisition"] >= 0.4 {
		agents = append(agents, "SyncValue") // LTV prediction guided targeting
	}

	if signalScores["product_promotion"] >= 0.3 {
		agents = append(agents, "SyncCreate") // Creative generation
	}

	if signalScores["nurture_engagement"] >= 0.3 {
		agents = append(agents, "SyncEngage") // Post-purchase nurture
	}

	// Default if no specific agent identified
	if len(agents) == 0 {
		agents = append(agents, "KIKI Platform")
	}

	return agents
}

// generateExplanation creates a human-readable attribution reason for XAI
//
// Example outputs:
// - "Customer clicked KIKI ad and purchased promoted product. 12% churn reduction by SyncEngage nurture."
// - "First-time customer acquired via KIKI-optimized bidding (SyncFlow). LTV prediction: $450."
// - "Repeat customer re-engaged through SyncEngage email flow. Product promoted by SyncCreate."
func (u *UpliftCalculator) generateExplanation(
	decision *AttributionDecision,
	signalScores map[string]float64,
) string {
	components := []string{}

	// Ad touchpoint
	if signalScores["ad_touchpoint"] >= 0.3 {
		components = append(components, "Customer interacted with KIKI-managed ad campaign")
	}

	// Acquisition
	if signalScores["acquisition"] >= 0.4 {
		components = append(components, "New customer acquired via KIKI-optimized targeting")
	}

	// Product promotion
	if signalScores["product_promotion"] >= 0.3 {
		components = append(components, "Purchased product promoted by KIKI-generated creatives")
	}

	// Nurture engagement
	if signalScores["nurture_engagement"] >= 0.3 {
		components = append(components, "Re-engaged through SyncEngage nurture flow")
	}

	// Combine into narrative
	if len(components) == 0 {
		return fmt.Sprintf(
			"Attributed to KIKI with %.0f%% confidence. Order value $%.2f exceeded baseline $%.2f by $%.2f.",
			decision.Confidence*100, decision.OrderAmount, decision.BaselineRevenue,
			decision.IncrementalRevenue,
		)
	}

	explanation := fmt.Sprintf(
		"%s. Incremental revenue: $%.2f (%.0f%% uplift). Success fee: $%.2f.",
		joinComponents(components), decision.IncrementalRevenue,
		decision.UpliftPercentage, decision.SuccessFee,
	)

	return explanation
}

// Helper: Join components with proper grammar
func joinComponents(components []string) string {
	if len(components) == 0 {
		return ""
	}
	if len(components) == 1 {
		return components[0]
	}
	if len(components) == 2 {
		return components[0] + " and " + components[1]
	}

	// Multiple components: "A, B, and C"
	return fmt.Sprintf(
		"%s, and %s",
		joinWithCommas(components[:len(components)-1]),
		components[len(components)-1],
	)
}

func joinWithCommas(parts []string) string {
	result := ""
	for i, part := range parts {
		result += part
		if i < len(parts)-1 {
			result += ", "
		}
	}
	return result
}

// VerifyBaselineQuality checks if baseline data is sufficient for accurate attribution
//
// Requirements:
// - At least 30 orders in baseline calculation
// - Baseline period >= 3 months
// - Revenue variance < 50% (stable business)
//
// Returns: "high", "medium", or "low" quality rating
func (u *UpliftCalculator) VerifyBaselineQuality(
	totalOrders int,
	baselinePeriodDays int,
	revenueVariance float64,
) string {
	if totalOrders < 10 || baselinePeriodDays < 30 {
		return "low"
	}

	if totalOrders < 30 || baselinePeriodDays < 90 || revenueVariance > 0.50 {
		return "medium"
	}

	return "high"
}

// SimulateZeroRiskScenario calculates what client would pay under different performance scenarios
//
// Scenario 1: KIKI performs well (+30% uplift) → Client pays 20% of incremental
// Scenario 2: KIKI underperforms (-10% vs baseline) → Client pays $0 (Zero-Risk)
// Scenario 3: KIKI neutral (0% uplift) → Client pays $0
//
// This is used for sales demonstrations and client dashboards
func (u *UpliftCalculator) SimulateZeroRiskScenario(baselineRevenue float64) map[string]MonthlyUplift {
	scenarios := map[string]MonthlyUplift{}

	// Scenario 1: +30% uplift (strong performance)
	actualHigh := baselineRevenue * 1.30
	scenarios["high_performance"] = *u.CalculateMonthlyUplift(
		baselineRevenue, actualHigh, actualHigh, 100,
	)

	// Scenario 2: -10% decline (underperformance)
	actualLow := baselineRevenue * 0.90
	scenarios["underperformance"] = *u.CalculateMonthlyUplift(
		baselineRevenue, actualLow, actualLow, 80,
	)

	// Scenario 3: Neutral (no change)
	scenarios["neutral"] = *u.CalculateMonthlyUplift(
		baselineRevenue, baselineRevenue, baselineRevenue, 90,
	)

	return scenarios
}

// CalculateROI computes the client's return on investment
//
// ROI = (IncrementalRevenue - SuccessFee) / SuccessFee * 100
//
// Example: Client pays $1,000 fee, gains $5,000 incremental revenue
// ROI = ($5,000 - $1,000) / $1,000 * 100 = 400%
func (u *UpliftCalculator) CalculateROI(incrementalRevenue, successFee float64) float64 {
	if successFee == 0 {
		return 0.0
	}

	netGain := incrementalRevenue - successFee
	roi := (netGain / successFee) * 100

	return math.Round(roi*100) / 100 // Round to 2 decimal places
}

// MarshalAgentsJSON converts agent list to JSON for database storage
func MarshalAgentsJSON(agents []string) string {
	data, _ := json.Marshal(agents)
	return string(data)
}

// MarshalSignalScoresJSON converts signal scores map to JSON
func MarshalSignalScoresJSON(scores map[string]float64) string {
	data, _ := json.Marshal(scores)
	return string(data)
}
