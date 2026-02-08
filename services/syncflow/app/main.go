// SyncFlow – Real-Time Bidding Engine
// Gin-based API, <1ms latency
package app

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"
	"go.opentelemetry.io/otel"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// Global budget optimizer instance
var globalOptimizer *GlobalBudgetOptimizer

// SetGlobalOptimizer sets the global optimizer instance (called from main package)
func SetGlobalOptimizer(optimizer *GlobalBudgetOptimizer) {
	globalOptimizer = optimizer
}

// NewRouter returns a Gin engine with all routes registered
// Prometheus metrics
var (
	requestCount = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "syncflow_requests_total",
			Help: "Total requests",
		},
		[]string{"endpoint", "method"},
	)
	errorCount = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "syncflow_errors_total",
			Help: "Total errors",
		},
		[]string{"endpoint"},
	)
	bidExecutions = prometheus.NewCounter(
		prometheus.CounterOpts{
			Name: "syncflow_bid_executions_total",
			Help: "Total bid executions",
		},
	)
	requestLatency = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "syncflow_request_latency_seconds",
			Help:    "Request latency",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"endpoint"},
	)
)

func init() {
	prometheus.MustRegister(requestCount, errorCount, bidExecutions, requestLatency)
}

var tracer = otel.Tracer("syncflow")

func NewRouter() *gin.Engine {
	r := gin.Default()
	r.Use(otelgin.Middleware("syncflow"))
	r.Use(prometheusMiddleware)
	r.POST("/execute-bid", ExecuteBidHandler)
	r.POST("/allocate-budget", AllocateBudget)
	r.GET("/healthz", HealthCheck)
	r.GET("/metrics", gin.WrapH(promhttp.Handler()))
	r.GET("/budget-efficiency", BudgetEfficiencyHandler)
	return r
}

// BudgetEfficiencyHandler exposes current platform efficiency metrics
func BudgetEfficiencyHandler(c *gin.Context) {
	if globalOptimizer == nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{
			"error": "GlobalBudgetOptimizer not initialized",
		})
		return
	}

	report, err := globalOptimizer.GetEfficiencyReport(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, report)
}

func prometheusMiddleware(c *gin.Context) {
	start := time.Now()
	c.Next()
	endpoint := c.FullPath()
	method := c.Request.Method
	requestCount.WithLabelValues(endpoint, method).Inc()
	requestLatency.WithLabelValues(endpoint).Observe(time.Since(start).Seconds())
	if c.Writer.Status() >= 400 {
		errorCount.WithLabelValues(endpoint).Inc()
	}
}

// --- Clean Architecture: UseCase Layer ---

// gRPC server stub removed: no BidRequest/BidResponse in valuepb, and not used in this service.

func main() {
	// Initialize GlobalBudgetOptimizer
	syncValueAddr := getEnv("SYNCVALUE_ADDR", "localhost:50051")

	optimizer, err := NewGlobalBudgetOptimizer(OptimizerConfig{
		EfficiencyThreshold: 0.15,            // 15% deviation triggers reallocation
		ReallocationPercent: 0.20,            // Shift 20% of budget
		CheckInterval:       5 * time.Minute, // Run every 5 minutes
		SyncValueAddr:       syncValueAddr,
	})
	if err != nil {
		log.Fatalf("❌ Failed to initialize GlobalBudgetOptimizer: %v", err)
	}

	globalOptimizer = optimizer

	// Start background optimization
	if err := globalOptimizer.Start(); err != nil {
		log.Fatalf("❌ Failed to start GlobalBudgetOptimizer: %v", err)
	}
	defer globalOptimizer.Stop()

	// Start HTTP server
	app := NewRouter()
	srv := &http.Server{
		Addr:    ":8000",
		Handler: app,
	}

	// Graceful shutdown
	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("❌ Failed to start server: %v", err)
		}
	}()

	log.Println("✅ SyncFlow started on :8000 with GlobalBudgetOptimizer")

	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("🛑 Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatal("❌ Server forced to shutdown:", err)
	}

	log.Println("✅ Server exited")
}

func getEnv(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}
