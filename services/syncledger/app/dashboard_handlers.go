package app

import (
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"

	"syncledger/internal"
	models "syncledger/internal"
)

// GetClientLedgerHandler returns the "Revenue Engine Room" dashboard data
//
// Endpoint: GET /api/v1/ledger/client/:storeID
// Auth: x-internal-api-key
//
// Response:
//
//	{
//	  "store_id": 123,
//	  "baseline_revenue": 50000.00,
//	  "current_revenue": 75000.00,
//	  "incremental_revenue": 25000.00,
//	  "uplift_percentage": 50.0,
//	  "success_fees_accumulated": 5000.00,
//	  "total_orders": 150,
//	  "attributed_orders": 75,
//	  "attribution_rate": 50.0,
//	  "roi": 400.0,
//	  "top_contributing_agents": {"SyncFlow": 0.45, "SyncEngage": 0.30}
//	}
func GetClientLedgerHandler(db *gorm.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		storeIDStr := c.Param("storeID")
		storeID, err := strconv.Atoi(storeIDStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid store ID"})
			return
		}

		// Get baseline snapshot
		var baseline models.BaselineSnapshot
		if err := db.Where("store_id = ?", storeID).First(&baseline).Error; err != nil {
			if err == gorm.ErrRecordNotFound {
				c.JSON(http.StatusNotFound, gin.H{"error": "Store not found or baseline not established"})
				return
			}
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
			return
		}

		// Get all ledger entries for this store
		var entries []models.LedgerEntry
		db.Where("store_id = ?", storeID).Find(&entries)

		// Calculate aggregated metrics
		var (
			totalOrders      = len(entries)
			attributedOrders = 0
			totalIncremental = 0.0
			totalFees        = 0.0
		)

		for _, entry := range entries {
			if entry.AttributedToKIKI {
				attributedOrders++
				totalIncremental += entry.IncrementalRevenue
				totalFees += entry.SuccessFeeAmount
			}
		}

		attributionRate := 0.0
		if totalOrders > 0 {
			attributionRate = float64(attributedOrders) / float64(totalOrders) * 100
		}

		upliftPercentage := 0.0
		if baseline.BaselineRevenue > 0 {
			upliftPercentage = (baseline.CurrentRevenue - baseline.BaselineRevenue) / baseline.BaselineRevenue * 100
		}

		// Calculate ROI for client
		calculator := internal.NewUpliftCalculator()
		roi := calculator.CalculateROI(totalIncremental, totalFees)

		// Get top contributing agents (from attribution logs)
		agentContributions := getAgentContributions(db, storeID)

		c.JSON(http.StatusOK, gin.H{
			"store_id":                 storeID,
			"platform":                 baseline.Platform,
			"baseline_revenue":         baseline.BaselineRevenue,
			"current_revenue":          baseline.CurrentRevenue,
			"incremental_revenue":      totalIncremental,
			"uplift_percentage":        upliftPercentage,
			"success_fees_accumulated": totalFees,
			"total_orders":             totalOrders,
			"attributed_orders":        attributedOrders,
			"attribution_rate":         attributionRate,
			"roi":                      roi,
			"top_contributing_agents":  agentContributions,
			"last_updated":             baseline.LastSyncedAt,
		})
	}
}

// GetSettlementReportHandler generates the monthly OaaS invoice report
//
// Endpoint: GET /api/v1/ledger/settlement/:storeID/:year/:month
// Auth: x-internal-api-key
//
// Response:
//
//	{
//	  "store_id": 123,
//	  "billing_period": "2024-01",
//	  "baseline_revenue": 50000.00,
//	  "actual_revenue": 75000.00,
//	  "incremental_revenue": 25000.00,
//	  "success_fee": 5000.00,
//	  "orders_attributed": 75,
//	  "xai_explanation": "KIKI generated $25,000 in incremental revenue..."
//	}
func GetSettlementReportHandler(db *gorm.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		storeID, _ := strconv.Atoi(c.Param("storeID"))
		year, _ := strconv.Atoi(c.Param("year"))
		month, _ := strconv.Atoi(c.Param("month"))

		// Check if invoice already exists
		var existingInvoice models.SuccessFeeInvoice
		err := db.Where("store_id = ? AND billing_year = ? AND billing_month = ?",
			storeID, year, month).First(&existingInvoice).Error

		if err == nil {
			// Invoice already generated, return it
			c.JSON(http.StatusOK, formatInvoiceResponse(&existingInvoice))
			return
		}

		// Generate new settlement report
		startDate := time.Date(year, time.Month(month), 1, 0, 0, 0, 0, time.UTC)
		endDate := startDate.AddDate(0, 1, 0).Add(-time.Second)

		// Get baseline
		var baseline models.BaselineSnapshot
		if err := db.Where("store_id = ?", storeID).First(&baseline).Error; err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Baseline not found"})
			return
		}

		// Get ledger entries for period
		var entries []models.LedgerEntry
		db.Where("store_id = ? AND created_at BETWEEN ? AND ?",
			storeID, startDate, endDate).Find(&entries)

		// Aggregate metrics
		var (
			totalRevenue     = 0.0
			totalIncremental = 0.0
			totalFees        = 0.0
			attributedCount  = 0
		)

		for _, entry := range entries {
			totalRevenue += entry.OrderAmount
			if entry.AttributedToKIKI {
				attributedCount++
				totalIncremental += entry.IncrementalRevenue
				totalFees += entry.SuccessFeeAmount
			}
		}

		monthlyBaseline := baseline.BaselineRevenue / 12.0
		upliftPercentage := 0.0
		if monthlyBaseline > 0 {
			upliftPercentage = ((totalRevenue - monthlyBaseline) / monthlyBaseline) * 100
		}

		// Create invoice record
		invoice := &models.SuccessFeeInvoice{
			StoreID:                storeID,
			Platform:               baseline.Platform,
			BillingMonth:           month,
			BillingYear:            year,
			BaselineRevenue:        monthlyBaseline,
			ActualRevenue:          totalRevenue,
			IncrementalRevenue:     totalIncremental,
			UpliftPercentage:       upliftPercentage,
			SuccessFeePercentage:   20.0,
			SuccessFeeAmount:       totalFees,
			TotalOrdersAttrributed: attributedCount,
			Status:                 "draft",
			DueDate:                endDate.AddDate(0, 0, 30), // Due in 30 days
			GeneratedBy:            "system",
		}

		db.Create(invoice)

		// Update ledger entries with invoice ID
		db.Model(&models.LedgerEntry{}).
			Where("store_id = ? AND created_at BETWEEN ? AND ?", storeID, startDate, endDate).
			Update("invoice_id", invoice.ID)

		c.JSON(http.StatusOK, formatInvoiceResponse(invoice))
	}
}

// GetLiveAttributionHandler shows real-time attribution feed (for dashboard animation)
//
// Endpoint: GET /api/v1/ledger/attribution/live/:storeID
// Auth: x-internal-api-key
//
// Response: Last 10 attributed orders with XAI explanations
func GetLiveAttributionHandler(db *gorm.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		storeID, _ := strconv.Atoi(c.Param("storeID"))

		var entries []models.LedgerEntry
		db.Where("store_id = ? AND attributed_to_kiki = ?", storeID, true).
			Order("created_at DESC").
			Limit(10).
			Find(&entries)

		var attributions []gin.H
		for _, entry := range entries {
			attributions = append(attributions, gin.H{
				"order_id":            entry.PlatformOrderID,
				"order_amount":        entry.OrderAmount,
				"incremental_revenue": entry.IncrementalRevenue,
				"success_fee":         entry.SuccessFeeAmount,
				"confidence":          entry.AttributionConfidence,
				"attribution_reason":  entry.AttributionReason,
				"agents_involved":     entry.AgentsInvolved,
				"timestamp":           entry.CreatedAt,
			})
		}

		c.JSON(http.StatusOK, gin.H{
			"store_id":     storeID,
			"attributions": attributions,
			"count":        len(attributions),
		})
	}
}

// GetAuditTrailHandler exports the immutable ledger for compliance/transparency
//
// Endpoint: GET /api/v1/ledger/audit/:storeID?start_date=2024-01-01&end_date=2024-12-31
// Auth: x-internal-api-key
//
// Response: CSV export of all ledger entries with hashes
func GetAuditTrailHandler(db *gorm.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		storeID, _ := strconv.Atoi(c.Param("storeID"))
		startDate := c.Query("start_date")
		endDate := c.Query("end_date")

		query := db.Where("store_id = ?", storeID)

		if startDate != "" && endDate != "" {
			query = query.Where("created_at BETWEEN ? AND ?", startDate, endDate)
		}

		var entries []models.LedgerEntry
		query.Order("created_at ASC").Find(&entries)

		// Generate CSV
		csv := "EntryHash,OrderID,OrderAmount,IncrementalRevenue,SuccessFee,Confidence,Timestamp\n"
		for _, entry := range entries {
			csv += fmt.Sprintf("%s,%s,%.2f,%.2f,%.2f,%.2f,%s\n",
				entry.EntryHash,
				entry.PlatformOrderID,
				entry.OrderAmount,
				entry.IncrementalRevenue,
				entry.SuccessFeeAmount,
				entry.AttributionConfidence,
				entry.CreatedAt.Format(time.RFC3339),
			)
		}

		c.Header("Content-Type", "text/csv")
		c.Header("Content-Disposition", fmt.Sprintf("attachment; filename=ledger_audit_%d.csv", storeID))
		c.String(http.StatusOK, csv)
	}
}

// Helper: Format invoice for API response
func formatInvoiceResponse(invoice *models.SuccessFeeInvoice) gin.H {
	explanation := fmt.Sprintf(
		"KIKI generated $%.2f in incremental revenue for %d-%02d, "+
			"representing a %.1f%% uplift over your baseline of $%.2f. "+
			"Total attributed orders: %d. Success fee (20%%): $%.2f.",
		invoice.IncrementalRevenue, invoice.BillingYear, invoice.BillingMonth,
		invoice.UpliftPercentage, invoice.BaselineRevenue,
		invoice.TotalOrdersAttrributed, invoice.SuccessFeeAmount,
	)

	return gin.H{
		"invoice_id":          invoice.ID,
		"store_id":            invoice.StoreID,
		"billing_period":      fmt.Sprintf("%d-%02d", invoice.BillingYear, invoice.BillingMonth),
		"baseline_revenue":    invoice.BaselineRevenue,
		"actual_revenue":      invoice.ActualRevenue,
		"incremental_revenue": invoice.IncrementalRevenue,
		"uplift_percentage":   invoice.UpliftPercentage,
		"success_fee":         invoice.SuccessFeeAmount,
		"orders_attributed":   invoice.TotalOrdersAttrributed,
		"status":              invoice.Status,
		"due_date":            invoice.DueDate,
		"xai_explanation":     explanation,
		"attribution_stats":   invoice.AttributionStats,
		"top_agents":          invoice.TopContributingAgents,
	}
}

// Helper: Get agent contribution breakdown
func getAgentContributions(db *gorm.DB, storeID int) map[string]float64 {
	var logs []models.AttributionLog
	db.Where("store_id = ?", storeID).Find(&logs)

	contributions := map[string]float64{
		"SyncFlow":   0.0,
		"SyncValue":  0.0,
		"SyncCreate": 0.0,
		"SyncEngage": 0.0,
	}

	for _, log := range logs {
		contributions["SyncFlow"] += log.SyncFlowContribution
		contributions["SyncValue"] += log.SyncValueContribution
		contributions["SyncCreate"] += log.SyncCreateContribution
		contributions["SyncEngage"] += log.SyncEngageContribution
	}

	// Normalize to percentages
	total := contributions["SyncFlow"] + contributions["SyncValue"] + contributions["SyncCreate"] + contributions["SyncEngage"]
	if total > 0 {
		for agent := range contributions {
			contributions[agent] = (contributions[agent] / total) * 100
		}
	}

	return contributions
}
