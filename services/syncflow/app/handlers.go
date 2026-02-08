package app

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// BidRequest represents a bid execution request
// ...existing code...
type BidRequest struct {
	UserID  string                 `json:"user_id" binding:"required"`
	Context map[string]interface{} `json:"context" binding:"required"`
}

type BidResponse struct {
	Status       string  `json:"status"`
	UserID       string  `json:"user_id"`
	Bid          float64 `json:"bid"`
	OriginalBid  float64 `json:"original_bid,omitempty"`  // Requested bid before MarginGuardian
	PredictedLTV float64 `json:"predicted_ltv,omitempty"` // Customer lifetime value
	MaxCPA       float64 `json:"max_cpa,omitempty"`       // Maximum allowed cost per acquisition
	RiskLevel    string  `json:"risk_level,omitempty"`    // safe, moderate, high, capped, rejected
	Explanation  string  `json:"explanation,omitempty"`   // Why bid was approved/capped/rejected
}

type BudgetRequest struct {
	CampaignID string  `json:"campaign_id" binding:"required"`
	Amount     float64 `json:"amount" binding:"required"`
}

type BudgetResponse struct {
	Status     string  `json:"status"`
	CampaignID string  `json:"campaign_id"`
	Allocated  float64 `json:"allocated"`
}

func ExecuteBid(c *gin.Context) {
	var req BidRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request: " + err.Error()})
		return
	}
	if req.UserID == "" || req.Context == nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "user_id and context are required"})
		return
	}
	bid := CalculateBid(req.Context)
	bidExecutions.Inc()
	resp := BidResponse{
		Status: "bid_executed",
		UserID: req.UserID,
		Bid:    bid,
	}
	c.JSON(http.StatusOK, resp)
}

func CalculateBid(ctx map[string]interface{}) float64 {
	if v, ok := ctx["priority"]; ok {
		if p, ok := v.(float64); ok && p > 0 {
			return 1.0 * p
		}
	}
	return 0.1
}

func AllocateBudget(c *gin.Context) {
	var req BudgetRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request: " + err.Error()})
		return
	}
	if req.CampaignID == "" || req.Amount <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "campaign_id and positive amount are required"})
		return
	}
	allocated := Allocate(req.CampaignID, req.Amount)
	resp := BudgetResponse{
		Status:     "budget_allocated",
		CampaignID: req.CampaignID,
		Allocated:  allocated,
	}
	c.JSON(http.StatusOK, resp)
}

func Allocate(campaignID string, amount float64) float64 {
	return amount * 0.95
}

func HealthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}
