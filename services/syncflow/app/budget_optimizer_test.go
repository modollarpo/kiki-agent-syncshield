package app

import (
	"context"
	"testing"

	budgetpb "kiki-agent-syncflow/shared/proto/budgetoptimizer"

	"github.com/stretchr/testify/assert"
	"google.golang.org/grpc"
	"github.com/stretchr/testify/mock"
)

// MockBudgetOptimizerClient mocks the gRPC client
type MockBudgetOptimizerClient struct {
	mock.Mock
}

func (m *MockBudgetOptimizerClient) GetPlatformLTV(ctx context.Context, req *budgetpb.PlatformLTVRequest, opts ...grpc.CallOption) (*budgetpb.PlatformLTVResponse, error) {
	args := m.Called(ctx, req)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*budgetpb.PlatformLTVResponse), args.Error(1)
}

func (m *MockBudgetOptimizerClient) SendBudgetAlert(ctx context.Context, req *budgetpb.BudgetAlertRequest, opts ...grpc.CallOption) (*budgetpb.BudgetAlertResponse, error) {
	args := m.Called(ctx, req)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*budgetpb.BudgetAlertResponse), args.Error(1)
}

func (m *MockBudgetOptimizerClient) RecordBudgetReallocation(ctx context.Context, req *budgetpb.BudgetReallocationRequest, opts ...grpc.CallOption) (*budgetpb.BudgetReallocationResponse, error) {
	args := m.Called(ctx, req)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*budgetpb.BudgetReallocationResponse), args.Error(1)
}

// TestGlobalBudgetOptimizer_CalculateAverageEfficiency tests efficiency calculation
func TestGlobalBudgetOptimizer_CalculateAverageEfficiency(t *testing.T) {
	optimizer := &GlobalBudgetOptimizer{
		Config: OptimizerConfig{
			EfficiencyThreshold: 0.15,
			ReallocationPercent: 0.20,
		},
	}

	efficiencies := []PlatformEfficiency{
		{Platform: budgetpb.Platform_PLATFORM_META, LTV: 450, CAC: 180, Efficiency: 2.5},
		{Platform: budgetpb.Platform_PLATFORM_TIKTOK, LTV: 420, CAC: 105, Efficiency: 4.0},
		{Platform: budgetpb.Platform_PLATFORM_GOOGLE, LTV: 480, CAC: 150, Efficiency: 3.2},
	}

	avgEfficiency := optimizer.calculateAverageEfficiency(efficiencies)

	// Expected: (2.5 + 4.0 + 3.2) / 3 = 3.23
	assert.InDelta(t, 3.23, avgEfficiency, 0.01, "Average efficiency should be 3.23")
}

// TestGlobalBudgetOptimizer_DetectUnderperformers tests 15% threshold
func TestGlobalBudgetOptimizer_DetectUnderperformers(t *testing.T) {
	optimizer := &GlobalBudgetOptimizer{
		Config: OptimizerConfig{
			EfficiencyThreshold: 0.15,
		},
	}

	efficiencies := []PlatformEfficiency{
		{Platform: budgetpb.Platform_PLATFORM_META, Efficiency: 2.5},
		{Platform: budgetpb.Platform_PLATFORM_TIKTOK, Efficiency: 4.0},
		{Platform: budgetpb.Platform_PLATFORM_GOOGLE, Efficiency: 3.2},
		{Platform: budgetpb.Platform_PLATFORM_LINKEDIN, Efficiency: 2.2},
	}

	avgEfficiency := 2.975
	underperformers := optimizer.detectUnderperformers(efficiencies, avgEfficiency)

	// Threshold: 2.975 - (2.975 * 0.15) = 2.529
	// Meta 2.5 < 2.529 ✅
	// LinkedIn 2.2 < 2.529 ✅
	assert.Equal(t, 2, len(underperformers), "Should detect 2 underperformers")
}

// TestGlobalBudgetOptimizer_FindBestPlatform tests highest efficiency selection
func TestGlobalBudgetOptimizer_FindBestPlatform(t *testing.T) {
	optimizer := &GlobalBudgetOptimizer{}

	efficiencies := []PlatformEfficiency{
		{Platform: budgetpb.Platform_PLATFORM_META, Efficiency: 2.5},
		{Platform: budgetpb.Platform_PLATFORM_TIKTOK, Efficiency: 4.0},
		{Platform: budgetpb.Platform_PLATFORM_GOOGLE, Efficiency: 3.2},
	}

	best := optimizer.findBestPlatform(efficiencies)

	assert.Equal(t, budgetpb.Platform_PLATFORM_TIKTOK, best.Platform, "TikTok should be best")
	assert.Equal(t, 4.0, best.Efficiency, "Best efficiency should be 4.0")
}

// TestGlobalBudgetOptimizer_ShiftBudget tests budget reallocation
func TestGlobalBudgetOptimizer_ShiftBudget(t *testing.T) {
	mockClient := new(MockBudgetOptimizerClient)

	optimizer := &GlobalBudgetOptimizer{
		syncValueClient: mockClient,
		Config: OptimizerConfig{
			ReallocationPercent: 0.20,
		},
	}

	from := PlatformEfficiency{
		Platform:    budgetpb.Platform_PLATFORM_META,
		Efficiency:  2.5,
		DailyBudget: 500.0,
	}

	to := PlatformEfficiency{
		Platform:   budgetpb.Platform_PLATFORM_TIKTOK,
		Efficiency: 4.0,
	}

	expectedShift := 100.0

	mockClient.On("RecordBudgetReallocation", mock.Anything, mock.MatchedBy(func(req *budgetpb.BudgetReallocationRequest) bool {
		return req.FromPlatform == budgetpb.Platform_PLATFORM_META &&
			req.ToPlatform == budgetpb.Platform_PLATFORM_TIKTOK &&
			req.AmountShifted == expectedShift
	})).Return(&budgetpb.BudgetReallocationResponse{
		Success:       true,
		LedgerEntryId: "test-001",
	}, nil)

	mockClient.On("SendBudgetAlert", mock.Anything, mock.Anything).Return(&budgetpb.BudgetAlertResponse{
		Success:        true,
		NotificationId: "notif-001",
	}, nil)

	err := optimizer.shiftBudget(context.Background(), from, to)

	assert.NoError(t, err, "Budget shift should succeed")
	mockClient.AssertExpectations(t)
}

// TestGlobalBudgetOptimizer_FullOptimizationCycle end-to-end test
func TestGlobalBudgetOptimizer_FullOptimizationCycle(t *testing.T) {
	mockClient := new(MockBudgetOptimizerClient)

	optimizer := &GlobalBudgetOptimizer{
		syncValueClient: mockClient,
		Config: OptimizerConfig{
			EfficiencyThreshold: 0.15,
			ReallocationPercent: 0.20,
		},
	}

	platforms := []budgetpb.Platform{
		budgetpb.Platform_PLATFORM_META,
		budgetpb.Platform_PLATFORM_GOOGLE,
		budgetpb.Platform_PLATFORM_TIKTOK,
		budgetpb.Platform_PLATFORM_LINKEDIN,
		budgetpb.Platform_PLATFORM_AMAZON,
		budgetpb.Platform_PLATFORM_MICROSOFT,
	}

	ltvMap := map[budgetpb.Platform]float64{
		budgetpb.Platform_PLATFORM_META:      450.0,
		budgetpb.Platform_PLATFORM_GOOGLE:    480.0,
		budgetpb.Platform_PLATFORM_TIKTOK:    420.0,
		budgetpb.Platform_PLATFORM_LINKEDIN:  440.0,
		budgetpb.Platform_PLATFORM_AMAZON:    460.0,
		budgetpb.Platform_PLATFORM_MICROSOFT: 470.0,
	}

	for _, platform := range platforms {
		mockClient.On("GetPlatformLTV", mock.Anything, mock.MatchedBy(func(req *budgetpb.PlatformLTVRequest) bool {
			return req.Platform == platform
		})).Return(&budgetpb.PlatformLTVResponse{
			Platform:   platform,
			AverageLtv: ltvMap[platform],
			SampleSize: 1000,
		}, nil)
	}

	mockClient.On("RecordBudgetReallocation", mock.Anything, mock.Anything).Return(&budgetpb.BudgetReallocationResponse{
		Success: true,
	}, nil)

	mockClient.On("SendBudgetAlert", mock.Anything, mock.Anything).Return(&budgetpb.BudgetAlertResponse{
		Success: true,
	}, nil)

	err := optimizer.OptimizeBudgetAllocation(context.Background())

	assert.NoError(t, err, "Full cycle should succeed")
	mockClient.AssertExpectations(t)
}
