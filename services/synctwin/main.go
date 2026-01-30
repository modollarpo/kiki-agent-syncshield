// SyncTwin – Shadow Simulation Mode
package main

import (
	"encoding/json"
	"math/rand"
	"net/http"
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

func main() {
	rand.Seed(time.Now().UnixNano())
	http.HandleFunc("/simulate", simulationHandler)
	http.HandleFunc("/healthz", healthHandler)
	http.ListenAndServe(":8007", nil)
}
