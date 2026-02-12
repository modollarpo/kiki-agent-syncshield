// SyncTwin – Shadow Simulation Mode
package main

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"net/http"
	"os"
	"time"
)

type SimulationRequest struct {
	BidAmount   float64 `json:"bid_amount"`
	Impressions int     `json:"impressions"`
	Platform    string  `json:"platform"`
}

type SimulationResult struct {
	SuccessRate        float64    `json:"success_rate"`
	ConfidenceInterval [2]float64 `json:"confidence_interval"`
	ProjectedRevenue   float64    `json:"projected_revenue"`
}

func runMonteCarlo(req SimulationRequest) SimulationResult {
	var wins int
	var totalRevenue float64
	for i := 0; i < 10000; i++ {
		win := rand.Float64() < 0.5 // 50% win rate stub
		if win {
			wins++
			totalRevenue += req.BidAmount * 1.2 // stub multiplier
		}
	}
	mean := float64(wins) / 10000.0
	ciLow := mean - 0.05
	ciHigh := mean + 0.05
	return SimulationResult{
		SuccessRate:        mean,
		ConfidenceInterval: [2]float64{ciLow, ciHigh},
		ProjectedRevenue:   totalRevenue,
	}
}

func simulationHandler(w http.ResponseWriter, r *http.Request) {
	var req SimulationRequest
	json.NewDecoder(r.Body).Decode(&req)
	result := runMonteCarlo(req)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(`{"status": "ok"}`))
}

// New: /simulate-strategy endpoint for OaaS dashboard
type SimulateStrategyRequest struct {
	Strategy string  `json:"strategy"`
	Budget   float64 `json:"budget"`
}
type SimulateStrategyResponse struct {
	ConfidenceScore          float64        `json:"confidence_score"`
	RiskProfile              string         `json:"risk_profile"`
	ProjectedNetProfitUplift float64        `json:"projected_net_profit_uplift"`
	SimulationID             string         `json:"simulation_id"`
	Details                  map[string]any `json:"details"`
}

func simulateStrategyHandler(w http.ResponseWriter, r *http.Request) {
	var req SimulateStrategyRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "invalid request", http.StatusBadRequest)
		return
	}
	confidence := 0.85 + rand.Float64()*0.13 // 0.85-0.98
	risk := []string{"conservative", "moderate", "aggressive"}[rand.Intn(3)]
	uplift := req.Budget * (0.12 + rand.Float64()*0.18) // 12-30% of budget
	resp := SimulateStrategyResponse{
		ConfidenceScore:          round2(confidence),
		RiskProfile:              risk,
		ProjectedNetProfitUplift: round2(uplift),
		SimulationID:             uuid(),
		Details: map[string]any{
			"strategy":  req.Strategy,
			"budget":    req.Budget,
			"simulated": true,
			"notes":     "This is a mock simulation. Replace with real ML logic.",
		},
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func round2(f float64) float64 {
	return float64(int(f*100)) / 100
}

func uuid() string {
	b := make([]byte, 16)
	rand.Read(b)
	return fmt.Sprintf("%x-%x-%x-%x-%x", b[0:4], b[4:6], b[6:8], b[8:10], b[10:])
}

func main() {
	rand.Seed(time.Now().UnixNano())
	http.HandleFunc("/simulate", simulationHandler)
	http.HandleFunc("/simulate-strategy", simulateStrategyHandler)
	http.HandleFunc("/healthz", healthHandler)
	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}
	http.ListenAndServe(":"+port, nil)
}
