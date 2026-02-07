package internal

import (
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// LedgerEntry represents a single immutable financial transaction record
//
// This is the core "Truth Ledger" that proves KIKI's value
//
// NET PROFIT MODEL UPDATES:
// - Added ad spend tracking fields (AdSpendForOrder, BaselineAdSpend, IncrementalAdSpend)
// - Added NetProfitUplift field (revenue increase - ad spend increase)
// - SuccessFeeAmount now based on NetProfitUplift, not IncrementalRevenue
type LedgerEntry struct {
	ID        uint      `gorm:"primaryKey" json:"id"`
	EntryHash string    `gorm:"uniqueIndex;not null" json:"entry_hash"` // SHA-256 hash for immutability
	CreatedAt time.Time `json:"created_at"`

	// Store & Platform
	StoreID  int    `gorm:"index;not null" json:"store_id"`
	Platform string `gorm:"type:varchar(50);not null" json:"platform"` // shopify, woocommerce, etc.

	// Order Details (from CMS webhook)
	OrderID         int     `gorm:"not null" json:"order_id"` // Internal order ID
	PlatformOrderID string  `gorm:"index;not null" json:"platform_order_id"`
	OrderAmount     float64 `gorm:"type:decimal(12,2);not null" json:"order_amount"` // Total order value

	// Attribution Data
	AttributedToKIKI      bool    `gorm:"not null;default:false" json:"attributed_to_kiki"`
	AttributionConfidence float64 `gorm:"type:decimal(3,2);not null" json:"attribution_confidence"` // 0.0-1.0

	// Net Profit Model Fields (NEW)
	IncrementalRevenue float64 `gorm:"type:decimal(12,2);default:0.00" json:"incremental_revenue"` // Gross revenue uplift
	BaselineRevenue    float64 `gorm:"type:decimal(12,2);not null" json:"baseline_revenue"`        // Pre-KIKI historical average
	UpliftPercentage   float64 `gorm:"type:decimal(5,2)" json:"uplift_percentage"`                 // (Current - Baseline) / Baseline * 100

	// Ad Spend Tracking (NEW for Net Profit Model)
	AdSpendForOrder    float64 `gorm:"type:decimal(12,2);default:0.00" json:"ad_spend_for_order"`   // Ad spend attributed to this order (CPA × 1)
	BaselineAdSpend    float64 `gorm:"type:decimal(12,2);default:0.00" json:"baseline_ad_spend"`    // Historical avg ad spend per order
	IncrementalAdSpend float64 `gorm:"type:decimal(12,2);default:0.00" json:"incremental_ad_spend"` // AdSpendForOrder - BaselineAdSpend
	NetProfitUplift    float64 `gorm:"type:decimal(12,2);default:0.00" json:"net_profit_uplift"`    // IncrementalRevenue - IncrementalAdSpend

	// Success Fee Calculation (based on Net Profit, NOT gross revenue)
	SuccessFeeAmount float64 `gorm:"type:decimal(12,2);default:0.00" json:"success_fee_amount"` // 20% of NetProfitUplift
	FeeApplicable    bool    `gorm:"not null;default:false" json:"fee_applicable"`

	// Campaign Attribution (which KIKI actions influenced this sale)
	CampaignID   *string `json:"campaign_id"`   // SyncFlow campaign ID
	CreativeID   *string `json:"creative_id"`   // SyncCreate creative ID
	TouchpointID *string `json:"touchpoint_id"` // Ad click/impression ID

	// Metadata for XAI (Explainability)
	AttributionReason string `gorm:"type:text" json:"attribution_reason"` // Human-readable explanation
	AgentsInvolved    string `gorm:"type:jsonb" json:"agents_involved"`   // JSON array: ["SyncValue", "SyncFlow", "SyncEngage"]

	// Invoice Tracking
	InvoiceID      *uint      `json:"invoice_id"`                                               // Foreign key to SuccessFeeInvoice
	InvoiceStatus  string     `gorm:"type:varchar(20);default:'pending'" json:"invoice_status"` // pending, invoiced, paid
	SettlementDate *time.Time `json:"settlement_date"`
}

// BeforeCreate hook to generate immutable hash
func (l *LedgerEntry) BeforeCreate(tx *gorm.DB) error {
	// Generate UUID-based hash for immutability
	l.EntryHash = uuid.New().String()
	return nil
}

func (LedgerEntry) TableName() string {
	return "ledger_entries"
}

// BaselineSnapshot stores the "Pre-KIKI" historical performance metrics
//
// Used to calculate real-time uplift: Current Revenue - Baseline = Incremental
//
// NET PROFIT MODEL UPDATES:
// - Added BaselineAdSpend (historical avg monthly ad spend)
// - Added CurrentAdSpend (running total of ad spend in current period)
// - Added BaselineProfit (BaselineRevenue - BaselineAdSpend)
// - Used for: NetProfitUplift = (CurrentRevenue - CurrentAdSpend) - (BaselineRevenue - BaselineAdSpend)
type BaselineSnapshot struct {
	ID        uint      `gorm:"primaryKey" json:"id"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`

	StoreID  int    `gorm:"uniqueIndex;not null" json:"store_id"`
	Platform string `gorm:"type:varchar(50);not null" json:"platform"`

	// Baseline Metrics (calculated from 12-month historical data)
	BaselineRevenue        float64 `gorm:"type:decimal(12,2);not null" json:"baseline_revenue"`
	BaselineOrders         int     `gorm:"not null" json:"baseline_orders"`
	BaselineAvgOrderValue  float64 `gorm:"type:decimal(10,2)" json:"baseline_avg_order_value"`
	BaselineRepeatRate     float64 `gorm:"type:decimal(5,2)" json:"baseline_repeat_rate"` // Percentage
	BaselineConversionRate float64 `gorm:"type:decimal(5,2)" json:"baseline_conversion_rate"`

	// Ad Spend Baselines (NEW for Net Profit Model)
	BaselineAdSpend        float64 `gorm:"type:decimal(12,2);default:0.00" json:"baseline_ad_spend"`         // Historical avg monthly ad spend
	BaselineMonthlyAdSpend float64 `gorm:"type:decimal(12,2);default:0.00" json:"baseline_monthly_ad_spend"` // Average monthly spend (12-month avg)
	BaselineProfit         float64 `gorm:"type:decimal(12,2);default:0.00" json:"baseline_profit"`           // BaselineRevenue - BaselineAdSpend

	// Current Period Ad Spend (NEW)
	CurrentAdSpend float64 `gorm:"type:decimal(12,2);default:0.00" json:"current_ad_spend"` // Running total of ad spend this month
	CurrentProfit  float64 `gorm:"type:decimal(12,2);default:0.00" json:"current_profit"`   // CurrentRevenue - CurrentAdSpend

	// Calculation Period
	CalculationStartDate time.Time `gorm:"not null" json:"calculation_start_date"` // e.g., 12 months ago
	CalculationEndDate   time.Time `gorm:"not null" json:"calculation_end_date"`   // e.g., KIKI install date
	TotalOrdersAnalyzed  int       `json:"total_orders_analyzed"`
	DataQuality          string    `gorm:"type:varchar(20);default:'high'" json:"data_quality"` // high, medium, low

	// KIKI Performance Comparison
	CurrentRevenue float64 `gorm:"type:decimal(12,2);default:0.00" json:"current_revenue"`
	CurrentOrders  int     `gorm:"default:0" json:"current_orders"`

	// Uplift Summary (with Net Profit)
	TotalIncrementalRevenue float64 `gorm:"type:decimal(12,2);default:0.00" json:"total_incremental_revenue"`  // Gross revenue uplift
	TotalIncrementalAdSpend float64 `gorm:"type:decimal(12,2);default:0.00" json:"total_incremental_ad_spend"` // Ad spend increase (NEW)
	TotalNetProfitUplift    float64 `gorm:"type:decimal(12,2);default:0.00" json:"total_net_profit_uplift"`    // Revenue uplift - Ad spend increase (NEW)
	TotalSuccessFees        float64 `gorm:"type:decimal(12,2);default:0.00" json:"total_success_fees"`         // 20% of TotalNetProfitUplift (NEW)

	// Last updated from SyncValue
	LastSyncedAt time.Time `json:"last_synced_at"`
}

func (BaselineSnapshot) TableName() string {
	return "baseline_snapshots"
}

// AttributionLog stores detailed attribution decision logs for debugging/transparency
type AttributionLog struct {
	ID        uint      `gorm:"primaryKey" json:"id"`
	CreatedAt time.Time `json:"created_at"`

	LedgerEntryID uint `gorm:"index;not null" json:"ledger_entry_id"`
	StoreID       int  `gorm:"index;not null" json:"store_id"`
	OrderID       int  `gorm:"index;not null" json:"order_id"`

	// Attribution Decision Process
	DecisionEngine   string  `gorm:"type:varchar(50)" json:"decision_engine"` // "multi_signal_v1", "ml_model_v2"
	SignalScores     string  `gorm:"type:jsonb" json:"signal_scores"`         // {"ad_touchpoint": 0.5, "acquisition": 0.5, "promotion": 0.3}
	FinalConfidence  float64 `gorm:"type:decimal(3,2);not null" json:"final_confidence"`
	ThresholdApplied float64 `gorm:"type:decimal(3,2);default:0.70" json:"threshold_applied"` // Confidence threshold

	// Agent Contributions (which agents influenced this sale)
	SyncValueContribution  float64 `gorm:"type:decimal(3,2)" json:"syncvalue_contribution"`  // LTV prediction accuracy
	SyncFlowContribution   float64 `gorm:"type:decimal(3,2)" json:"syncflow_contribution"`   // Bid optimization impact
	SyncCreateContribution float64 `gorm:"type:decimal(3,2)" json:"synccreate_contribution"` // Creative performance
	SyncEngageContribution float64 `gorm:"type:decimal(3,2)" json:"syncengage_contribution"` // Nurture flow impact

	// XAI (Explainability) Output
	Explanation           string  `gorm:"type:text" json:"explanation"`                     // Human-readable attribution reason
	CounterfactualRevenue float64 `gorm:"type:decimal(12,2)" json:"counterfactual_revenue"` // Estimated revenue without KIKI

	// Audit Trail
	AttributedBy string     `gorm:"type:varchar(100)" json:"attributed_by"` // System or manual override
	ReviewedBy   *string    `json:"reviewed_by"`                            // Admin who reviewed (if manual override)
	ReviewedAt   *time.Time `json:"reviewed_at"`
}

func (AttributionLog) TableName() string {
	return "attribution_logs"
}

// SuccessFeeInvoice represents a monthly billing period for OaaS
//
// NET PROFIT MODEL UPDATES:
// - Added baseline_ad_spend (historical avg monthly ad spend)
// - Added actual_ad_spend (ad spend for current billing period)
// - Added incremental_ad_spend (actual - baseline)
// - Added net_profit_uplift (incremental_revenue - incremental_ad_spend)
// - success_fee_amount now = net_profit_uplift × 20% (NOT incremental_revenue × 20%)
type SuccessFeeInvoice struct {
	ID        uint      `gorm:"primaryKey" json:"id"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`

	StoreID  int    `gorm:"index;not null" json:"store_id"`
	Platform string `gorm:"type:varchar(50);not null" json:"platform"`

	// Billing Period
	BillingMonth int `gorm:"not null" json:"billing_month"` // 1-12
	BillingYear  int `gorm:"not null" json:"billing_year"`  // 2024, 2025, etc.

	// Revenue Summary (Gross Model)
	BaselineRevenue    float64 `gorm:"type:decimal(12,2);not null" json:"baseline_revenue"`
	ActualRevenue      float64 `gorm:"type:decimal(12,2);not null" json:"actual_revenue"`
	IncrementalRevenue float64 `gorm:"type:decimal(12,2);not null" json:"incremental_revenue"` // Actual - Baseline
	UpliftPercentage   float64 `gorm:"type:decimal(5,2)" json:"uplift_percentage"`             // (Incremental / Baseline) * 100

	// Ad Spend Summary (NEW for Net Profit Model)
	BaselineAdSpend      float64 `gorm:"type:decimal(12,2);default:0.00" json:"baseline_ad_spend"`      // Historical avg monthly ad spend
	ActualAdSpend        float64 `gorm:"type:decimal(12,2);default:0.00" json:"actual_ad_spend"`        // Actual ad spend this month (Meta + Google)
	IncrementalAdSpend   float64 `gorm:"type:decimal(12,2);default:0.00" json:"incremental_ad_spend"`   // Actual - Baseline
	AdSpendUpliftPercent float64 `gorm:"type:decimal(5,2);default:0.00" json:"ad_spend_uplift_percent"` // (Incremental / Baseline) * 100

	// Net Profit Calculation (THE KEY METRIC)
	NetProfitUplift        float64 `gorm:"type:decimal(12,2);default:0.00" json:"net_profit_uplift"`        // IncrementalRevenue - IncrementalAdSpend
	BaselineProfit         float64 `gorm:"type:decimal(12,2);default:0.00" json:"baseline_profit"`          // BaselineRevenue - BaselineAdSpend
	ActualProfit           float64 `gorm:"type:decimal(12,2);default:0.00" json:"actual_profit"`            // ActualRevenue - ActualAdSpend
	NetProfitUpliftPercent float64 `gorm:"type:decimal(5,2);default:0.00" json:"net_profit_uplift_percent"` // (NetUplift / BaselineProfit) * 100

	// Success Fee Calculation (based on Net Profit, NOT gross revenue)
	SuccessFeePercentage   float64 `gorm:"type:decimal(4,2);default:20.00" json:"success_fee_percentage"` // Default 20%
	SuccessFeeAmount       float64 `gorm:"type:decimal(12,2);not null" json:"success_fee_amount"`         // NetProfitUplift × 20%
	ClientNetGain          float64 `gorm:"type:decimal(12,2);default:0.00" json:"client_net_gain"`        // NetProfitUplift - SuccessFeeAmount
	ClientROI              float64 `gorm:"type:decimal(5,2);default:0.00" json:"client_roi"`              // ClientNetGain / SuccessFeeAmount
	TotalOrdersAttrributed int     `gorm:"not null" json:"total_orders_attributed"`

	// Attribution Breakdown (XAI)
	AttributionStats      string `gorm:"type:jsonb" json:"attribution_stats"`       // {"high_confidence": 50, "medium": 20, "low": 5}
	TopContributingAgents string `gorm:"type:jsonb" json:"top_contributing_agents"` // {"SyncFlow": 0.45, "SyncEngage": 0.30}

	// Invoice Status
	Status     string     `gorm:"type:varchar(20);default:'draft'" json:"status"` // draft, sent, paid, disputed
	SentAt     *time.Time `json:"sent_at"`
	PaidAt     *time.Time `json:"paid_at"`
	DueDate    time.Time  `json:"due_date"`
	InvoiceURL *string    `json:"invoice_url"` // Link to PDF invoice

	// Client Communication
	ClientNotified     bool       `gorm:"default:false" json:"client_notified"`
	NotificationSentAt *time.Time `json:"notification_sent_at"`
	ExplanationSent    bool       `gorm:"default:false" json:"explanation_sent"` // Whether XAI report was sent

	// Audit
	GeneratedBy string     `gorm:"type:varchar(100)" json:"generated_by"` // System or manual
	ApprovedBy  *string    `json:"approved_by"`
	ApprovedAt  *time.Time `json:"approved_at"`
}

func (SuccessFeeInvoice) TableName() string {
	return "success_fee_invoices"
}
