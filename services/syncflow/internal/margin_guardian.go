package internal

import (
	"context"
	"fmt"
	"log"
	"math"
	"time"
)

// MarginGuardian enforces profit-safe bidding constraints
//
// Purpose: Prevent KIKI from losing money on ad spend
// Strategy: Only bid if CPA < LTV (Customer Lifetime Value)
//
// Example:
//   - LTV = $150 (predicted customer lifetime value)
//   - Max CPA = $150 * 0.70 = $105 (70% safety margin)
//   - If current bid would exceed $105, REJECT or cap bid
//
// Integration with Net Profit Model:
//   - Net Profit = (Revenue - Baseline Revenue) - (Ad Spend - Baseline Ad Spend)
//   - If we overspend on ads, Net Profit goes negative
//   - Client doesn't pay KIKI → Revenue loss
//   - MarginGuardian prevents this by enforcing CPA < LTV
type MarginGuardian struct {
	// SafetyMargin is the percentage of LTV to use as max CPA (default 0.70 = 70%)
	SafetyMargin float64

	// MinLTVRequired is the minimum LTV to allow bidding (default $50)
	MinLTVRequired float64

	// MaxBidCap is the absolute maximum bid allowed regardless of LTV (default $100)
	MaxBidCap float64

	// LTVServiceURL is the endpoint to fetch predicted LTV from SyncValue
	LTVServiceURL string
}

// NewMarginGuardian creates a new MarginGuardian with default settings
func NewMarginGuardian() *MarginGuardian {
	return &MarginGuardian{
		SafetyMargin:   0.70,                            // Use 70% of LTV as max CPA
		MinLTVRequired: 50.0,                            // Minimum $50 LTV to bid
		MaxBidCap:      100.0,                           // Never bid more than $100
		LTVServiceURL:  "http://syncvalue:8080/predict", // SyncValue gRPC/HTTP endpoint
	}
}

// BidDecision represents the guardian's decision on a bid
type BidDecision struct {
	Approved      bool    // Whether bid is approved
	OriginalBid   float64 // Original requested bid amount
	ApprovedBid   float64 // Approved bid (may be capped)
	MaxAllowedCPA float64 // Maximum CPA based on LTV
	PredictedLTV  float64 // Predicted customer LTV
	Reason        string  // Explanation for decision
	RiskLevel     string  // "safe", "moderate", "high", "rejected"
}

// EvaluateBid checks if a bid is profit-safe
//
// Flow:
// 1. Fetch predicted LTV from SyncValue
// 2. Calculate max allowed CPA = LTV * SafetyMargin
// 3. Compare requested bid to max CPA
// 4. Approve, cap, or reject bid
//
// Example:
//
//	userID: "12345"
//	requestedBid: $80
//	→ SyncValue predicts LTV = $150
//	→ Max CPA = $150 * 0.70 = $105
//	→ $80 < $105 → APPROVED
//
// Example 2:
//
//	requestedBid: $120
//	→ SyncValue predicts LTV = $100
//	→ Max CPA = $100 * 0.70 = $70
//	→ $120 > $70 → REJECTED (or cap to $70)
func (mg *MarginGuardian) EvaluateBid(ctx context.Context, userID string, requestedBid float64) (*BidDecision, error) {
	start := time.Now()
	defer func() {
		log.Printf("🛡️ MarginGuardian: Evaluated bid for user %s in %v", userID, time.Since(start))
	}()

	// Step 1: Fetch predicted LTV from SyncValue
	predictedLTV, err := mg.fetchLTV(ctx, userID)
	if err != nil {
		// If LTV service is unavailable, use conservative default
		log.Printf("⚠️ MarginGuardian: LTV fetch failed for %s, using default $50: %v", userID, err)
		predictedLTV = mg.MinLTVRequired
	}

	// Step 2: Calculate max allowed CPA
	maxAllowedCPA := predictedLTV * mg.SafetyMargin

	// Apply absolute max bid cap
	if maxAllowedCPA > mg.MaxBidCap {
		maxAllowedCPA = mg.MaxBidCap
	}

	// Step 3: Check if LTV meets minimum threshold
	if predictedLTV < mg.MinLTVRequired {
		return &BidDecision{
			Approved:      false,
			OriginalBid:   requestedBid,
			ApprovedBid:   0.0,
			MaxAllowedCPA: maxAllowedCPA,
			PredictedLTV:  predictedLTV,
			Reason:        fmt.Sprintf("LTV $%.2f below minimum threshold $%.2f", predictedLTV, mg.MinLTVRequired),
			RiskLevel:     "rejected",
		}, nil
	}

	// Step 4: Evaluate bid against max CPA
	decision := &BidDecision{
		OriginalBid:   requestedBid,
		MaxAllowedCPA: maxAllowedCPA,
		PredictedLTV:  predictedLTV,
	}

	if requestedBid <= maxAllowedCPA {
		// Bid is within safe limits
		decision.Approved = true
		decision.ApprovedBid = requestedBid

		// Calculate risk level
		utilizationPct := (requestedBid / maxAllowedCPA) * 100
		if utilizationPct <= 50 {
			decision.RiskLevel = "safe"
			decision.Reason = fmt.Sprintf("Bid $%.2f well below max CPA $%.2f (%.0f%% utilization)", requestedBid, maxAllowedCPA, utilizationPct)
		} else if utilizationPct <= 80 {
			decision.RiskLevel = "moderate"
			decision.Reason = fmt.Sprintf("Bid $%.2f within safe range (%.0f%% of max CPA $%.2f)", requestedBid, utilizationPct, maxAllowedCPA)
		} else {
			decision.RiskLevel = "high"
			decision.Reason = fmt.Sprintf("Bid $%.2f approaching max CPA $%.2f (%.0f%% utilization)", requestedBid, maxAllowedCPA, utilizationPct)
		}
	} else {
		// Bid exceeds max CPA - cap it
		decision.Approved = true                    // Still approve, but cap the bid
		decision.ApprovedBid = maxAllowedCPA * 0.95 // Cap at 95% of max to leave margin
		decision.RiskLevel = "capped"
		decision.Reason = fmt.Sprintf("Original bid $%.2f exceeds max CPA $%.2f, capped to $%.2f", requestedBid, maxAllowedCPA, decision.ApprovedBid)

		log.Printf("⚠️ MarginGuardian: Capped bid for user %s from $%.2f to $%.2f (LTV: $%.2f)", userID, requestedBid, decision.ApprovedBid, predictedLTV)
	}

	return decision, nil
}

// fetchLTV calls SyncValue to get predicted customer lifetime value
//
// Example request to SyncValue:
//
//	POST http://syncvalue:8080/predict
//	{
//	  "user_id": "12345",
//	  "features": {
//	    "avg_order_value": 50.0,
//	    "purchase_frequency": 2.5,
//	    "recency_days": 30
//	  }
//	}
//
// Example response:
//
//	{
//	  "user_id": "12345",
//	  "predicted_ltv": 150.0,
//	  "confidence": 0.85,
//	  "model_version": "dRNN_v2"
//	}
func (mg *MarginGuardian) fetchLTV(ctx context.Context, userID string) (float64, error) {
	// TODO: Implement actual gRPC/HTTP call to SyncValue
	// For now, return a stub value based on heuristics

	// Stub implementation: Use simple heuristic
	// In production, this would call SyncValue's LTV prediction API
	// Example:
	// conn, err := grpc.Dial(mg.LTVServiceURL, grpc.WithInsecure())
	// client := pb.NewLTVServiceClient(conn)
	// resp, err := client.PredictLTV(ctx, &pb.LTVRequest{UserId: userID})

	// Stub: Return a random LTV between $50-$200 based on userID hash
	// In production, replace with actual SyncValue call
	hashValue := hashString(userID)
	ltvValue := 50.0 + math.Mod(float64(hashValue), 150.0)

	log.Printf("📊 MarginGuardian: Fetched LTV $%.2f for user %s (stub)", ltvValue, userID)
	return ltvValue, nil
}

// CalculateOptimalBid calculates the optimal bid to maximize profit
//
// Strategy:
// - Start with max allowed CPA (LTV * SafetyMargin)
// - Adjust based on competition, conversion rate, and risk tolerance
// - Return bid that maximizes expected Net Profit
//
// Formula:
//
//	Expected Net Profit = (LTV × Win Probability) - Bid
//	Optimal Bid = argmax(Expected Net Profit)
func (mg *MarginGuardian) CalculateOptimalBid(ctx context.Context, userID string, competitionLevel float64) (float64, error) {
	predictedLTV, err := mg.fetchLTV(ctx, userID)
	if err != nil || predictedLTV < mg.MinLTVRequired {
		return 0.0, fmt.Errorf("LTV below threshold or unavailable")
	}

	maxBid := predictedLTV * mg.SafetyMargin

	// Adjust for competition (1.0 = average, >1.0 = high competition)
	// Higher competition → bid closer to max
	adjustedBid := maxBid * (0.6 + (0.3 * math.Min(competitionLevel, 1.5)))

	// Apply absolute cap
	if adjustedBid > mg.MaxBidCap {
		adjustedBid = mg.MaxBidCap
	}

	log.Printf("💡 MarginGuardian: Optimal bid for user %s = $%.2f (LTV: $%.2f, Competition: %.2fx)", userID, adjustedBid, predictedLTV, competitionLevel)
	return adjustedBid, nil
}

// GetMetrics returns current MarginGuardian metrics for monitoring
func (mg *MarginGuardian) GetMetrics() map[string]float64 {
	return map[string]float64{
		"safety_margin_pct": mg.SafetyMargin * 100,
		"min_ltv_required":  mg.MinLTVRequired,
		"max_bid_cap":       mg.MaxBidCap,
	}
}

// hashString is a simple hash function for stub LTV generation
func hashString(s string) int {
	hash := 0
	for i := 0; i < len(s); i++ {
		hash = (hash * 31) + int(s[i])
	}
	return hash
}
