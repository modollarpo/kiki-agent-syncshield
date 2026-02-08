package app

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"kiki-agent-syncflow/internal"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
)

var (
	BidRequestCount = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "syncflow_bid_requests_total",
			Help: "Total bid requests received",
		},
		[]string{"endpoint", "method"},
	)
	BidErrorCount = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "syncflow_bid_errors_total",
			Help: "Total bid errors",
		},
		[]string{"endpoint"},
	)
	BidLatency = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name: "syncflow_bid_latency_seconds",
			Help: "Bid request latency",
		},
		[]string{"endpoint"},
	)
	BidsCapped = prometheus.NewCounter(
		prometheus.CounterOpts{
			Name: "syncflow_bids_capped_total",
			Help: "Total bids capped by MarginGuardian",
		},
	)
	BidsRejected = prometheus.NewCounter(
		prometheus.CounterOpts{
			Name: "syncflow_bids_rejected_total",
			Help: "Total bids rejected by MarginGuardian",
		},
	)
)

// Global MarginGuardian instance
var marginGuardian *internal.MarginGuardian

func init() {
	prometheus.MustRegister(BidRequestCount, BidErrorCount, BidLatency, BidsCapped, BidsRejected)
	marginGuardian = internal.NewMarginGuardian()
}

// POST /execute-bid
// Enhanced with MarginGuardian to enforce profit-safe bidding
func ExecuteBidHandler(c *gin.Context) {
	start := time.Now()
	BidRequestCount.WithLabelValues("/execute-bid", "POST").Inc()
	
	var req BidRequest
	if err := c.ShouldBindJSON(&req); err != nil || req.UserID == "" || req.Context == nil {
		BidErrorCount.WithLabelValues("/execute-bid").Inc()
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid bid request: user_id and context required"})
		return
	}

	// Calculate initial bid based on context
	initialBid := CalculateBid(req.Context)

	// CRITICAL: MarginGuardian validates bid is profit-safe
	// Prevents KIKI from losing money if CPA > LTV
	ctx := context.Background()
	decision, err := marginGuardian.EvaluateBid(ctx, req.UserID, initialBid)
	if err != nil {
		BidErrorCount.WithLabelValues("/execute-bid").Inc()
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "MarginGuardian evaluation failed",
			"details": err.Error(),
		})
		return
	}

	// Track MarginGuardian actions
	if !decision.Approved {
		BidsRejected.Inc()
		c.JSON(http.StatusOK, gin.H{
			"status": "bid_rejected",
			"user_id": req.UserID,
			"reason": decision.Reason,
			"requested_bid": decision.OriginalBid,
			"predicted_ltv": decision.PredictedLTV,
			"max_allowed_cpa": decision.MaxAllowedCPA,
		})
		BidLatency.WithLabelValues("/execute-bid").Observe(time.Since(start).Seconds())
		return
	}

	if decision.RiskLevel == "capped" {
		BidsCapped.Inc()
	}

	// Execute bid with approved amount
	resp := BidResponse{
		Status:       fmt.Sprintf("bid_executed_%s", decision.RiskLevel),
		UserID:       req.UserID,
		Bid:          decision.ApprovedBid,
		OriginalBid:  decision.OriginalBid,
		PredictedLTV: decision.PredictedLTV,
		MaxCPA:       decision.MaxAllowedCPA,
		RiskLevel:    decision.RiskLevel,
		Explanation:  decision.Reason,
	}

	c.JSON(http.StatusOK, resp)
	BidLatency.WithLabelValues("/execute-bid").Observe(time.Since(start).Seconds())
}

// Real service-to-service call to SyncValue with tracing and metrics

// func CallSyncValueLTV(ctx trace.SpanContext, userID string) (*LTVPredictionResponse, error) {
// 	// Prometheus metric for integration calls
// 	integrationCount := prometheus.NewCounter(prometheus.CounterOpts{
// 		Name: "syncflow_syncvalue_ltv_total",
// 		Help: "Total SyncValue LTV API calls",
// 	})
// 	prometheus.MustRegister(integrationCount)
// 	integrationCount.Inc()
// 	tracer := otel.Tracer("syncflow/handlers_bid")
// 	_, span := tracer.Start(ctx, "CallSyncValueLTV")
// 	defer span.End()
//  // Real HTTP call to SyncValue
//  reqBody := map[string]interface{}{"user_id": userID, "features": map[string]interface{}{}}
//  bodyBytes, _ := json.Marshal(reqBody)
//  httpReq, _ := http.NewRequest("POST", "http://syncvalue:8000/predict-ltv", bytes.NewReader(bodyBytes))
//  httpReq.Header.Set("Content-Type", "application/json")
//  client := &http.Client{Timeout: 2 * time.Second}
//  resp, err := client.Do(httpReq)
//  if err != nil {
//      log.Printf("SyncValue HTTP error: %v", err)
//      return nil, err
//  }
//  defer resp.Body.Close()
//  if resp.StatusCode != http.StatusOK {
//      log.Printf("SyncValue returned status %d", resp.StatusCode)
//      return nil, err
//  }
//  // var ltvResp LTVPredictionResponse
//  if err := json.NewDecoder(resp.Body).Decode(&ltvResp); err != nil {
//      log.Printf("SyncValue decode error: %v", err)
//      return nil, err
//  }
//  return &ltvResp, nil
// }
