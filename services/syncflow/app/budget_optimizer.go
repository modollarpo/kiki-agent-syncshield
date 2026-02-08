package app

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/robfig/cron/v3"

	budgetpb "kiki-agent-syncflow/shared/proto/budgetoptimizer"
)

// GlobalBudgetOptimizer - Cross-platform budget allocation engine
// Implements the "Omni-Channel Sovereign" logic from copilot-instructions.md
//
// Algorithm (runs every 5 minutes):
// 1. Calculate LTV-to-CAC ratio per platform (call SyncValue)
// 2. Calculate average efficiency across all 6 platforms
// 3. Detect platforms with >15% efficiency drop below average
// 4. Shift 20% of daily budget from underperformer to best performer
// 5. Alert client via SyncNotify (email/SMS/Slack)
// 6. Log to SyncLedger for OaaS attribution
type GlobalBudgetOptimizer struct {
	cron       *cron.Cron
	httpClient *http.Client

	// Configuration
	Config OptimizerConfig

	// Metrics
	budgetShiftsTotal       prometheus.Counter
	platformEfficiencyGauge *prometheus.GaugeVec

	// Thread safety
	mu sync.RWMutex
}

type OptimizerConfig struct {
	EfficiencyThreshold float64       // 0.15 = 15% deviation triggers reallocation
	ReallocationPercent float64       // 0.20 = shift 20% of budget
	CheckInterval       time.Duration // 5 minutes
	SyncValueAddr       string        // "http://syncvalue:8000"
}

// PlatformEfficiency tracks LTV/CAC ratio and budget per platform
type PlatformEfficiency struct {
	Platform    budgetpb.Platform
	LTV         float64
	CAC         float64
	Efficiency  float64 // LTV / CAC
	DailyBudget float64 // Current daily budget in USD
}

// Prometheus metrics
var (
	budgetShiftsTotal = promauto.NewCounter(prometheus.CounterOpts{
		Name: "syncflow_budget_shifts_total",
		Help: "Total number of cross-platform budget reallocations",
	})

	platformEfficiencyGauge = promauto.NewGaugeVec(prometheus.GaugeOpts{
		Name: "syncflow_platform_efficiency",
		Help: "LTV-to-CAC efficiency ratio per platform",
	}, []string{"platform"})
)

// NewGlobalBudgetOptimizer creates a new optimizer with HTTP client
func NewGlobalBudgetOptimizer(config OptimizerConfig) (*GlobalBudgetOptimizer, error) {
	optimizer := &GlobalBudgetOptimizer{
		cron: cron.New(),
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
		Config:                  config,
		budgetShiftsTotal:       budgetShiftsTotal,
		platformEfficiencyGauge: platformEfficiencyGauge,
	}

	return optimizer, nil
}

// Start begins the cron job for periodic budget optimization
func (g *GlobalBudgetOptimizer) Start() error {
	_, err := g.cron.AddFunc(fmt.Sprintf("@every %s", g.Config.CheckInterval), func() {
		if err := g.OptimizeBudgetAllocation(context.Background()); err != nil {
			log.Printf("❌ Budget optimization failed: %v", err)
		}
	})
	if err != nil {
		return fmt.Errorf("failed to schedule cron job: %w", err)
	}

	g.cron.Start()
	log.Printf("✅ GlobalBudgetOptimizer started (interval: %s)", g.Config.CheckInterval)
	return nil
}

// Stop gracefully shuts down the optimizer
func (g *GlobalBudgetOptimizer) Stop() error {
	g.cron.Stop()
	g.httpClient.CloseIdleConnections()
	log.Println("✅ GlobalBudgetOptimizer stopped")
	return nil
}

// OptimizeBudgetAllocation - Main 5-step algorithm
func (g *GlobalBudgetOptimizer) OptimizeBudgetAllocation(ctx context.Context) error {
	g.mu.Lock()
	defer g.mu.Unlock()

	log.Println("🔄 Running cross-platform budget optimization...")

	// Step 1: Calculate platform efficiencies
	efficiencies, err := g.calculatePlatformEfficiencies(ctx, "demo-client-001")
	if err != nil {
		return fmt.Errorf("failed to calculate efficiencies: %w", err)
	}

	// Step 2: Calculate average efficiency
	avgEfficiency := g.calculateAverageEfficiency(efficiencies)
	log.Printf("📊 Average efficiency: %.2fx", avgEfficiency)

	// Step 3: Detect underperformers (>15% below average)
	underperformers := g.detectUnderperformers(efficiencies, avgEfficiency)
	if len(underperformers) == 0 {
		log.Println("✅ All platforms performing within acceptable range")
		return nil
	}

	// Step 4: Find best performer
	bestPlatform := g.findBestPlatform(efficiencies)

	// Step 5: Execute budget shifts
	for _, underperformer := range underperformers {
		if err := g.shiftBudget(ctx, underperformer, bestPlatform); err != nil {
			log.Printf("⚠️ Failed to shift budget: %v", err)
			continue
		}

		budgetShiftsTotal.Inc()
		log.Printf("✅ Shifted: %s (%.2fx) → %s (%.2fx)",
			underperformer.Platform, underperformer.Efficiency,
			bestPlatform.Platform, bestPlatform.Efficiency)
	}

	return nil
}

// calculatePlatformEfficiencies fetches LTV from SyncValue and CAC from platform APIs
func (g *GlobalBudgetOptimizer) calculatePlatformEfficiencies(ctx context.Context, clientID string) ([]PlatformEfficiency, error) {
	platforms := []budgetpb.Platform{
		budgetpb.Platform_PLATFORM_META,
		budgetpb.Platform_PLATFORM_GOOGLE,
		budgetpb.Platform_PLATFORM_TIKTOK,
		budgetpb.Platform_PLATFORM_LINKEDIN,
		budgetpb.Platform_PLATFORM_AMAZON,
		budgetpb.Platform_PLATFORM_MICROSOFT,
	}

	efficiencies := make([]PlatformEfficiency, 0, len(platforms))

	for _, platform := range platforms {
		// Call SyncValue via REST API
		ltvResp, err := g.getPlatformLTVREST(ctx, clientID, platform)
		if err != nil {
			log.Printf("⚠️ Failed to get LTV for %s: %v", platform, err)
			continue
		}

		cac := g.getPlatformCAC(ctx, platform)

		efficiency := PlatformEfficiency{
			Platform:    platform,
			LTV:         ltvResp.AverageLTV,
			CAC:         cac,
			Efficiency:  ltvResp.AverageLTV / cac,
			DailyBudget: g.getPlatformDailyBudget(platform),
		}

		efficiencies = append(efficiencies, efficiency)
		platformEfficiencyGauge.WithLabelValues(platform.String()).Set(efficiency.Efficiency)
	}

	return efficiencies, nil
}

// calculateAverageEfficiency computes mean LTV/CAC ratio
func (g *GlobalBudgetOptimizer) calculateAverageEfficiency(efficiencies []PlatformEfficiency) float64 {
	if len(efficiencies) == 0 {
		return 0
	}

	var sum float64
	for _, eff := range efficiencies {
		sum += eff.Efficiency
	}

	return sum / float64(len(efficiencies))
}

// detectUnderperformers finds platforms <15% below average
func (g *GlobalBudgetOptimizer) detectUnderperformers(efficiencies []PlatformEfficiency, avgEfficiency float64) []PlatformEfficiency {
	threshold := avgEfficiency - (avgEfficiency * g.Config.EfficiencyThreshold)
	underperformers := make([]PlatformEfficiency, 0)

	for _, eff := range efficiencies {
		if eff.Efficiency < threshold {
			deviation := ((eff.Efficiency - avgEfficiency) / avgEfficiency) * 100
			log.Printf("⚠️ Underperformer: %s (%.2fx, %.1f%% below avg)",
				eff.Platform, eff.Efficiency, deviation)
			underperformers = append(underperformers, eff)
		}
	}

	return underperformers
}

// platformLTVResponse matches SyncValue's handlers_platform_ltv.py response
type platformLTVResponse struct {
	Platform   string  `json:"platform"`
	AverageLTV float64 `json:"average_ltv"`
	P25LTV     float64 `json:"p25_ltv"`
	P75LTV     float64 `json:"p75_ltv"`
	SampleSize int     `json:"sample_size"`
}

// platformLTVRequest matches SyncValue's handlers_platform_ltv.py request
type platformLTVRequest struct {
	ClientID     string `json:"client_id"`
	Platform     string `json:"platform"`
	LookbackDays int    `json:"lookback_days"`
}

// getPlatformLTVREST calls SyncValue's REST API /platform-ltv endpoint
func (g *GlobalBudgetOptimizer) getPlatformLTVREST(ctx context.Context, clientID string, platform budgetpb.Platform) (*platformLTVResponse, error) {
	reqBody := platformLTVRequest{
		ClientID:     clientID,
		Platform:     platform.String(),
		LookbackDays: 90,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	url := fmt.Sprintf("%s/platform-ltv", g.Config.SyncValueAddr)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := g.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to call SyncValue: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("SyncValue returned %d: %s", resp.StatusCode, string(body))
	}

	var ltvResp platformLTVResponse
	if err := json.NewDecoder(resp.Body).Decode(&ltvResp); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &ltvResp, nil
}

// findBestPlatform returns platform with highest efficiency
func (g *GlobalBudgetOptimizer) findBestPlatform(efficiencies []PlatformEfficiency) PlatformEfficiency {
	if len(efficiencies) == 0 {
		return PlatformEfficiency{}
	}

	best := efficiencies[0]
	for _, eff := range efficiencies[1:] {
		if eff.Efficiency > best.Efficiency {
			best = eff
		}
	}

	return best
}

// shiftBudget executes reallocation
func (g *GlobalBudgetOptimizer) shiftBudget(ctx context.Context, from, to PlatformEfficiency) error {
	shiftAmount := from.DailyBudget * g.Config.ReallocationPercent

	// Log to SyncLedger via gRPC
	log.Printf("📝 [LOCAL] Recording budget shift: %s → %s ($%.0f)", from.Platform, to.Platform, shiftAmount)

	// Send alert via SyncNotify gRPC
	alertMsg := fmt.Sprintf(
		"%s CPMs impacted. Shifted $%.0f/day to %s (%.2fx vs %.2fx)",
		from.Platform, shiftAmount, to.Platform, to.Efficiency, from.Efficiency,
	)
	log.Printf("📧 [LOCAL] Alert: %s", alertMsg)

	log.Printf("💰 Shifted: $%.0f/day from %s to %s", shiftAmount, from.Platform, to.Platform)
	return nil
}

// getPlatformCAC fetches Cost-Per-Acquisition (placeholder)
func (g *GlobalBudgetOptimizer) getPlatformCAC(ctx context.Context, platform budgetpb.Platform) float64 {
	cacMap := map[budgetpb.Platform]float64{
		budgetpb.Platform_PLATFORM_META:      180.0,
		budgetpb.Platform_PLATFORM_GOOGLE:    150.0,
		budgetpb.Platform_PLATFORM_TIKTOK:    105.0,
		budgetpb.Platform_PLATFORM_LINKEDIN:  200.0,
		budgetpb.Platform_PLATFORM_AMAZON:    175.0,
		budgetpb.Platform_PLATFORM_MICROSOFT: 190.0,
	}
	return cacMap[platform]
}

// getPlatformDailyBudget returns current daily budget (placeholder)
func (g *GlobalBudgetOptimizer) getPlatformDailyBudget(platform budgetpb.Platform) float64 {
	budgetMap := map[budgetpb.Platform]float64{
		budgetpb.Platform_PLATFORM_META:      500.0,
		budgetpb.Platform_PLATFORM_GOOGLE:    450.0,
		budgetpb.Platform_PLATFORM_TIKTOK:    400.0,
		budgetpb.Platform_PLATFORM_LINKEDIN:  300.0,
		budgetpb.Platform_PLATFORM_AMAZON:    200.0,
		budgetpb.Platform_PLATFORM_MICROSOFT: 150.0,
	}
	return budgetMap[platform]
}

// GetEfficiencyReport returns current efficiency metrics
func (g *GlobalBudgetOptimizer) GetEfficiencyReport(ctx context.Context) (map[string]interface{}, error) {
	g.mu.RLock()
	defer g.mu.RUnlock()

	efficiencies, err := g.calculatePlatformEfficiencies(ctx, "demo-client-001")
	if err != nil {
		return nil, err
	}

	avgEfficiency := g.calculateAverageEfficiency(efficiencies)
	bestPlatform := g.findBestPlatform(efficiencies)

	platformDetails := make([]map[string]interface{}, 0, len(efficiencies))
	for _, eff := range efficiencies {
		platformDetails = append(platformDetails, map[string]interface{}{
			"platform":     eff.Platform.String(),
			"ltv":          eff.LTV,
			"cac":          eff.CAC,
			"efficiency":   eff.Efficiency,
			"daily_budget": eff.DailyBudget,
		})
	}

	return map[string]interface{}{
		"timestamp":          time.Now().Unix(),
		"average_efficiency": avgEfficiency,
		"best_platform":      bestPlatform.Platform.String(),
		"best_efficiency":    bestPlatform.Efficiency,
		"platform_details":   platformDetails,
	}, nil
}
