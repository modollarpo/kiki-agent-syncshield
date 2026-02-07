package main

import (
	"context"
	"log"
	"net"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"google.golang.org/grpc"
	"google.golang.org/grpc/health"
	"google.golang.org/grpc/health/grpc_health_v1"
	"google.golang.org/grpc/reflection"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"syncledger/app"
	models "syncledger/internal"
	pb "syncledger/proto"
)

const (
grpcPort = ":50053" // gRPC server port
httpPort = ":8090"  // HTTP server port (for dashboard API and health checks)
)

// Prometheus metrics
var (
	revenueAttributed = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "syncledger_revenue_attributed_total",
			Help: "Total incremental revenue attributed to KIKI",
		},
		[]string{"store_id", "platform"},
	)
	successFeeCalculated = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "syncledger_success_fee_calculated_total",
			Help: "Total success fees calculated (20% of incremental)",
		},
		[]string{"store_id"},
	)
	attributionLatency = prometheus.NewHistogram(
		prometheus.HistogramOpts{
			Name:    "syncledger_attribution_latency_ms",
			Help:    "Latency of attribution calculations in milliseconds",
			Buckets: prometheus.LinearBuckets(0, 5, 20), // 0-100ms in 5ms increments
		},
	)
)

func init() {
prometheus.MustRegister(revenueAttributed)
prometheus.MustRegister(successFeeCalculated)
prometheus.MustRegister(attributionLatency)
}

func main() {
	log.Println("🚀 Starting SyncLedger™ - Automated OaaS Auditor")

	// Initialize database
	db, err := initDB()
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	// Auto-migrate database models
	if err := db.AutoMigrate(
		&models.LedgerEntry{},
		&models.BaselineSnapshot{},
		&models.AttributionLog{},
		&models.SuccessFeeInvoice{},
	); err != nil {
		log.Fatalf("Failed to migrate database: %v", err)
	}
	log.Println("✅ Database connected and migrated")

	// Initialize gRPC server
	grpcServer := grpc.NewServer(
		grpc.UnaryInterceptor(loggingInterceptor),
	)

	// Register SyncLedgerService
	ledgerService := app.NewLedgerService(db)
	pb.RegisterSyncLedgerServiceServer(grpcServer, ledgerService)

	// Register health check
	healthServer := health.NewServer()
	grpc_health_v1.RegisterHealthServer(grpcServer, healthServer)

	// Register reflection for grpcurl
	reflection.Register(grpcServer)

	// Start gRPC server in goroutine
	var wg sync.WaitGroup
	wg.Add(2)

	go func() {
		defer wg.Done()
		lis, err := net.Listen("tcp", grpcPort)
		if err != nil {
			log.Fatalf("Failed to listen on %s: %v", grpcPort, err)
		}
		log.Printf("🔌 gRPC server listening on %s", grpcPort)
		if err := grpcServer.Serve(lis); err != nil {
			log.Fatalf("gRPC server failed: %v", err)
		}
	}()

	// Start HTTP server for dashboard API and metrics
	go func() {
		defer wg.Done()
		router := setupHTTPRouter(db)
		httpServer := &http.Server{
			Addr:    httpPort,
			Handler: router,
		}
		log.Printf("🌐 HTTP server listening on %s", httpPort)
		log.Println("📊 Dashboard API: http://localhost:8090/api/v1/ledger/client/{storeID}")
		log.Println("📈 Metrics: http://localhost:8090/metrics")
		log.Println("💚 Health: http://localhost:8090/healthz")
		if err := httpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("HTTP server failed: %v", err)
		}
	}()

	// Graceful shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("🛑 Shutting down SyncLedger™...")
	grpcServer.GracefulStop()
	log.Println("✅ SyncLedger™ stopped gracefully")
	wg.Wait()
}

func initDB() (*gorm.DB, error) {
	dsn := os.Getenv("DATABASE_URL")
	if dsn == "" {
		dsn = "postgres://kiki:password@postgres:5432/kiki_ledger?sslmode=disable"
	}
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		return nil, err
	}

	// Set connection pool settings
	sqlDB, err := db.DB()
	if err != nil {
		return nil, err
	}
	sqlDB.SetMaxIdleConns(10)
	sqlDB.SetMaxOpenConns(100)
	sqlDB.SetConnMaxLifetime(time.Hour)

	return db, nil
}

func setupHTTPRouter(db *gorm.DB) *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	router := gin.Default()

	// CORS middleware
	router.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type, x-internal-api-key")
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	})

	// Health check
	router.GET("/healthz", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "healthy", "service": "syncledger"})
	})

	// Prometheus metrics
	router.GET("/metrics", gin.WrapH(promhttp.Handler()))

	// Dashboard API
	apiGroup := router.Group("/api/v1/ledger")
	apiGroup.Use(authMiddleware())
	{
		// Client Revenue Engine Room (for dashboard)
		apiGroup.GET("/client/:storeID", app.GetClientLedgerHandler(db))
		// Monthly settlement report
		apiGroup.GET("/client/:storeID/:year/:month", app.GetSettlementReportHandler(db))
		// Real-time attribution status
		apiGroup.GET("/live/:storeID", app.GetLiveAttributionHandler(db))
		// Audit trail export (immutable ledger)
		apiGroup.GET("/audit/:storeID", app.GetAuditTrailHandler(db))
	}

	return router
}

func authMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		apiKey := c.GetHeader("x-internal-api-key")
		expectedKey := os.Getenv("KIKI_INTERNAL_API_KEY")
		if expectedKey == "" {
			expectedKey = "dev-internal-key-change-in-production"
		}
		if apiKey != expectedKey {
			c.JSON(403, gin.H{"error": "Invalid internal API key"})
			c.Abort()
			return
		}
		c.Next()
	}
}

func loggingInterceptor(
	ctx context.Context,
	req interface{},
	info *grpc.UnaryServerInfo,
	handler grpc.UnaryHandler,
) (interface{}, error) {
	start := time.Now()
	resp, err := handler(ctx, req)
	duration := time.Since(start)
	log.Printf("gRPC %s | %s | %v", info.FullMethod, duration, err)
	attributionLatency.Observe(float64(duration.Milliseconds()))
	return resp, err
}
