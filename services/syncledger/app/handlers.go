package app

import (
	"context"
	"log"
	"time"

	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"gorm.io/gorm"

	"syncledger/internal"
	models "syncledger/internal"
	pb "syncledger/proto"
)

// LedgerService implements the gRPC SyncLedgerService
type LedgerService struct {
	pb.UnimplementedSyncLedgerServiceServer
	db         *gorm.DB
	calculator *internal.UpliftCalculator
}

// NewLedgerService creates a new gRPC service instance
func NewLedgerService(db *gorm.DB) *LedgerService {
	return &LedgerService{
		db:         db,
		calculator: internal.NewUpliftCalculator(),
	}
}

// RecordIncrementalRevenue is called by SyncPortal when an order is attributed to KIKI
//
// gRPC Flow:
// 1. SyncPortal webhook receives order
// 2. Attribution engine calculates confidence (e.g., 0.85)
// 3. If confidence >= 0.70, call this method via gRPC
// 4. SyncLedger records entry and calculates success fee
//
// Example Request:
//
//	{
//	  "store_id": 123,
//	  "order_id": 456,
//	  "order_amount": {"units": 99, "nanos": 990000000},
//	  "incremental_amount": {"units": 29, "nanos": 990000000},
//	  "attribution_confidence": 0.85,
//	  "campaign_id": "campaign_123_meta"
//	}
func (s *LedgerService) RecordIncrementalRevenue(
	ctx context.Context,
	req *pb.IncrementalRevenueRequest,
) (*pb.IncrementalRevenueResponse, error) {
	log.Printf("📊 RecordIncrementalRevenue: Store %d, Order %d, Amount $%.2f, Confidence %.2f",
		req.StoreId, req.OrderId, moneyToFloat(req.OrderAmount), req.AttributionConfidence)

	// Validate request
	if req.StoreId == 0 || req.OrderId == 0 {
		return nil, status.Error(codes.InvalidArgument, "store_id and order_id are required")
	}
	if req.AttributionConfidence < 0.0 || req.AttributionConfidence > 1.0 {
		return nil, status.Error(codes.InvalidArgument, "attribution_confidence must be between 0.0 and 1.0")
	}

	// Get baseline snapshot for this store
	var baseline models.BaselineSnapshot
	if err := s.db.Where("store_id = ?", req.StoreId).First(&baseline).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, status.Errorf(codes.FailedPrecondition,
				"Baseline not found for store %d. Call UpdateBaselineMetrics first.", req.StoreId)
		}
		return nil, status.Errorf(codes.Internal, "Failed to fetch baseline: %v", err)
	}

	// Calculate attribution decision
	orderAmount := moneyToFloat(req.OrderAmount)

	// Build signal scores from request metadata
	signalScores := map[string]float64{
		"ad_touchpoint":      0.5, // From attribution engine
		"product_promotion":  0.3,
		"nurture_engagement": 0.2,
	}

	decision := s.calculator.CalculateAttribution(
		orderAmount,
		baseline.BaselineAvgOrderValue,
		float64(req.AttributionConfidence),
		signalScores,
	)

	// Create ledger entry (immutable record)
	entry := &models.LedgerEntry{
		StoreID:               int(req.StoreId),
		Platform:              req.Platform,
		OrderID:               int(req.OrderId),
		PlatformOrderID:       req.PlatformOrderId,
		OrderAmount:           orderAmount,
		AttributedToKIKI:      decision.IsAttributed,
		AttributionConfidence: float64(req.AttributionConfidence),
		IncrementalRevenue:    decision.IncrementalRevenue,
		BaselineRevenue:       baseline.BaselineAvgOrderValue,
		UpliftPercentage:      decision.UpliftPercentage,
		SuccessFeeAmount:      decision.SuccessFee,
		FeeApplicable:         decision.FeeApplicable,
		CampaignID:            stringPtr(req.CampaignId),
		AttributionReason:     decision.Reason,
		AgentsInvolved:        internal.MarshalAgentsJSON(decision.AgentsInvolved),
		InvoiceStatus:         "pending",
	}

	// Save to database
	if err := s.db.Create(entry).Error; err != nil {
		return nil, status.Errorf(codes.Internal, "Failed to create ledger entry: %v", err)
	}

	// Update baseline snapshot with current performance
	baseline.CurrentRevenue += orderAmount
	baseline.CurrentOrders += 1
	if decision.FeeApplicable {
		baseline.TotalIncrementalRevenue += decision.IncrementalRevenue
		baseline.TotalSuccessFees += decision.SuccessFee
	}
	baseline.LastSyncedAt = time.Now()
	s.db.Save(&baseline)

	// Create attribution log for transparency
	attrLog := &models.AttributionLog{
		LedgerEntryID:          entry.ID,
		StoreID:                int(req.StoreId),
		OrderID:                int(req.OrderId),
		DecisionEngine:         "multi_signal_v1",
		SignalScores:           internal.MarshalSignalScoresJSON(signalScores),
		FinalConfidence:        float64(req.AttributionConfidence),
		ThresholdApplied:       s.calculator.ConfidenceThreshold,
		SyncFlowContribution:   signalScores["ad_touchpoint"],
		SyncCreateContribution: signalScores["product_promotion"],
		SyncEngageContribution: signalScores["nurture_engagement"],
		Explanation:            decision.Reason,
		CounterfactualRevenue:  decision.Counterfactual,
		AttributedBy:           "system",
	}
	s.db.Create(attrLog)

	log.Printf("💰 Ledger Entry Created: ID %d, Incremental $%.2f, Fee $%.2f",
		entry.ID, entry.IncrementalRevenue, entry.SuccessFeeAmount)

	// Build response
	response := &pb.IncrementalRevenueResponse{
		Success:              decision.IsAttributed,
		CountedAsIncremental: decision.IsAttributed,
		SuccessFeeAmount:     floatToMoney(decision.SuccessFee),
		LedgerEntryId:        int32(entry.ID),
		InvoiceId:            "", // Set later when invoice is generated
		Explanation:          decision.Reason,
	}

	return response, nil
}

// CalculateSuccessFee generates the monthly OaaS settlement report
//
// Called by:
// - SyncPortal dashboard (end of month)
// - Admin invoice generation script
// - Client API for transparency
//
// Returns:
// - Baseline vs current revenue comparison
// - Total incremental revenue
// - Success fee (20% of incremental)
// - Attribution breakdown (XAI)
func (s *LedgerService) CalculateSuccessFee(
	ctx context.Context,
	req *pb.SuccessFeeRequest,
) (*pb.SuccessFeeResponse, error) {
	log.Printf("📅 CalculateSuccessFee: Store %d, Period %d-%02d",
		req.StoreId, req.Year, req.Month)

	// Get baseline
	var baseline models.BaselineSnapshot
	if err := s.db.Where("store_id = ?", req.StoreId).First(&baseline).Error; err != nil {
		return nil, status.Errorf(codes.NotFound, "Baseline not found for store %d", req.StoreId)
	}

	// Get all ledger entries for this billing period
	startDate := time.Date(int(req.Year), time.Month(req.Month), 1, 0, 0, 0, 0, time.UTC)
	endDate := startDate.AddDate(0, 1, 0).Add(-time.Second)

	var entries []models.LedgerEntry
	if err := s.db.Where("store_id = ? AND created_at BETWEEN ? AND ?",
		req.StoreId, startDate, endDate).Find(&entries).Error; err != nil {
		return nil, status.Errorf(codes.Internal, "Failed to fetch entries: %v", err)
	}

	// Aggregate metrics
	var (
		totalRevenue        float64
		totalIncremental    float64
		totalSuccessFees    float64
		attributedCount     int
		highConfidenceCount int
	)

	for _, entry := range entries {
		totalRevenue += entry.OrderAmount
		if entry.AttributedToKIKI {
			attributedCount++
			totalIncremental += entry.IncrementalRevenue
			totalSuccessFees += entry.SuccessFeeAmount
			if entry.AttributionConfidence >= 0.85 {
				highConfidenceCount++
			}
		}
	}

	// Calculate monthly baseline (annual baseline / 12)
	monthlyBaseline := baseline.BaselineRevenue / 12.0

	// Calculate uplift percentage
	var upliftPercentage float64
	if monthlyBaseline > 0 {
		upliftPercentage = ((totalRevenue - monthlyBaseline) / monthlyBaseline) * 100
	}

	// Build XAI attribution stats
	attributionStats := map[string]int32{
		"total_orders":      int32(len(entries)),
		"attributed_orders": int32(attributedCount),
		"high_confidence":   int32(highConfidenceCount),
		"medium_confidence": int32(attributedCount - highConfidenceCount),
	}

	log.Printf("📊 Settlement: Baseline $%.2f → Actual $%.2f (+%.1f%%), Fee $%.2f",
		monthlyBaseline, totalRevenue, upliftPercentage, totalSuccessFees)

	response := &pb.SuccessFeeResponse{
		Success:              true,
		BaselineRevenue:      floatToMoney(monthlyBaseline),
		CurrentRevenue:       floatToMoney(totalRevenue),
		IncrementalRevenue:   floatToMoney(totalIncremental),
		GrowthPercentage:     float32(upliftPercentage),
		SuccessFeeAmount:     floatToMoney(totalSuccessFees),
		TotalOrdersReviewed:  int32(len(entries)),
		AttributedOrderCount: int32(attributedCount),
		AttributionStats:     attributionStats,
		HighConfidenceCount:  int32(highConfidenceCount),
	}

	return response, nil
}

// GetOrderAttribution retrieves the attribution details for a specific order
//
// Used by:
// - Client dashboard ("Why was I charged for this order?")
// - Admin review panel
// - XAI explainability reports
func (s *LedgerService) GetOrderAttribution(
	ctx context.Context,
	req *pb.OrderAttributionRequest,
) (*pb.OrderAttributionResponse, error) {
	log.Printf("🔍 GetOrderAttribution: Order %d", req.OrderId)

	// Find ledger entry
	var entry models.LedgerEntry
	if err := s.db.Where("order_id = ?", req.OrderId).First(&entry).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, status.Errorf(codes.NotFound, "Order %d not found in ledger", req.OrderId)
		}
		return nil, status.Errorf(codes.Internal, "Failed to fetch order: %v", err)
	}

	// Get attribution log for detailed explanation
	var attrLog models.AttributionLog
	s.db.Where("ledger_entry_id = ?", entry.ID).First(&attrLog)

	response := &pb.OrderAttributionResponse{
		Success:               true,
		Attributed:            entry.AttributedToKIKI,
		Confidence:            float32(entry.AttributionConfidence),
		IncrementalRevenue:    floatToMoney(entry.IncrementalRevenue),
		SuccessFeeAmount:      floatToMoney(entry.SuccessFeeAmount),
		Explanation:           entry.AttributionReason,
		ContributingAgents:    entry.AgentsInvolved, // JSON string
		CounterfactualRevenue: floatToMoney(attrLog.CounterfactualRevenue),
	}

	return response, nil
}

// Helper: Convert protobuf Money to float64
func moneyToFloat(m *pb.Money) float64 {
	if m == nil {
		return 0.0
	}
	return float64(m.Units) + float64(m.Nanos)/1e9
}

// Helper: Convert float64 to protobuf Money
func floatToMoney(f float64) *pb.Money {
	units := int64(f)
	nanos := int32((f - float64(units)) * 1e9)
	return &pb.Money{
		Currency: "USD",
		Units:    units,
		Nanos:    nanos,
	}
}

// Helper: String pointer
func stringPtr(s string) *string {
	if s == "" {
		return nil
	}
	return &s
}

// RecordBudgetReallocation logs cross-platform budget shifts from GlobalBudgetOptimizer
//
// Called by: SyncFlow GlobalBudgetOptimizer
// Purpose: Track all budget reallocations for OaaS attribution
//
// Example Request:
//
//	{
//	  "client_id": "demo-client-001",
//	  "from_platform": "PLATFORM_META",
//	  "to_platform": "PLATFORM_TIKTOK",
//	  "amount_shifted": 100.00,
//	  "reason": "Efficiency drop: 2.50x vs 2.83x avg",
//	  "from_efficiency": 2.5,
//	  "to_efficiency": 4.0,
//	  "timestamp": 1738935567
//	}
func (s *LedgerService) RecordBudgetReallocation(
	ctx context.Context,
	req *pb.BudgetReallocationRequest,
) (*pb.BudgetReallocationResponse, error) {
	log.Printf("💰 RecordBudgetReallocation: %s → %s ($%.2f) - Reason: %s",
		req.FromPlatform, req.ToPlatform, req.AmountShifted, req.Reason)

	// Validate request
	if req.ClientId == "" {
		return nil, status.Error(codes.InvalidArgument, "client_id is required")
	}
	if req.AmountShifted <= 0 {
		return nil, status.Error(codes.InvalidArgument, "amount_shifted must be positive")
	}

	// Create budget reallocation log entry
	reallocationLog := map[string]interface{}{
		"client_id":       req.ClientId,
		"from_platform":   req.FromPlatform,
		"to_platform":     req.ToPlatform,
		"amount_shifted":  req.AmountShifted,
		"reason":          req.Reason,
		"from_efficiency": req.FromEfficiency,
		"to_efficiency":   req.ToEfficiency,
		"timestamp":       time.Unix(req.Timestamp, 0),
		"created_at":      time.Now(),
	}

	// Insert into budget_reallocation_log table
	// Note: Table will be created by migration script
	result := s.db.Table("budget_reallocation_log").Create(reallocationLog)
	if result.Error != nil {
		log.Printf("❌ Failed to record budget reallocation: %v", result.Error)
		return nil, status.Errorf(codes.Internal, "Failed to record reallocation: %v", result.Error)
	}

	// Get last insert ID
	var insertedID int64
	s.db.Raw("SELECT LAST_INSERT_ID()").Scan(&insertedID)

	log.Printf("✅ Budget reallocation recorded - Entry ID: %d", insertedID)

	return &pb.BudgetReallocationResponse{
		Success:       true,
		LedgerEntryId: int32(insertedID),
	}, nil
}
