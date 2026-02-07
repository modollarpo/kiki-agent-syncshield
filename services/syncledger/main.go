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
"syncledger/internal/models"
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
Failed to connect to database: %v", err)
}

// Auto-migrate database models
if err := db.AutoMigrate(
try{},
eSnapshot{},
Log{},
voice{},
); err != nil {
Failed to migrate database: %v", err)
}
log.Println("✅ Database connected and migrated")

// Initialize gRPC server
grpcServer := grpc.NewServer(
aryInterceptor(loggingInterceptor),
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
wg.Done()
err := net.Listen("tcp", grpcPort)
err != nil {
Failed to listen on %s: %v", grpcPort, err)
tf("🔌 gRPC server listening on %s", grpcPort)
err := grpcServer.Serve(lis); err != nil {
gRPC server failed: %v", err)

// Start HTTP server for dashboard API and metrics
go func() {
wg.Done()
:= setupHTTPRouter(db)
:= &http.Server{
   httpPort,
dler: router,
tf("🌐 HTTP server listening on %s", httpPort)
tln("📊 Dashboard API: http://localhost:8090/api/v1/ledger/client/{storeID}")
tln("📈 Metrics: http://localhost:8090/metrics")
tln("💚 Health: http://localhost:8090/healthz")
err := httpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
HTTP server failed: %v", err)

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
 = "postgres://kiki:password@postgres:5432/kiki_ledger?sslmode=disable"
}
db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
if err != nil {
 nil, err
}

// Set connection pool settings
sqlDB, err := db.DB()
if err != nil {
 nil, err
}
sqlDB.SetMaxIdleConns(10)
sqlDB.SetMaxOpenConns(100)
sqlDB.SetConn MaxLifetime(time.Hour)

return db, nil
}

func setupHTTPRouter(db *gorm.DB) *gin.Engine {
gin.SetMode(gin.ReleaseMode)
router := gin.Default()

// CORS middleware
router.Use(func(c *gin.Context) {
trol-Allow-Origin", "*")
trol-Allow-Methods", "GET, POST, OPTIONS")
trol-Allow-Headers", "Content-Type, x-internal-api-key")
c.Request.Method == "OPTIONS" {

ext()
})

// Health check
router.GET("/healthz", func(c *gin.Context) {
(200, gin.H{"status": "healthy", "service": "syncledger"})
})

// Prometheus metrics
router.GET("/metrics", gin.WrapH(promhttp.Handler()))

// Dashboard API
apiGroup := router.Group("/api/v1/ledger")
apiGroup.Use(authMiddleware())
{
Client Revenue Engine Room (for dashboard)
t/:storeID", app.GetClientLedgerHandler(db))
Monthly settlement report
t/:storeID/:year/:month", app.GetSettlementReportHandler(db))
Real-time attribution status
/live/:storeID", app.GetLiveAttributionHandler(db))
Audit trail export (immutable ledger)
app.GetAuditTrailHandler(db))
}

return router
}

func authMiddleware() gin.HandlerFunc {
return func(c *gin.Context) {
 := c.GetHeader("x-internal-api-key")
 := os.Getenv("KIKI_INTERNAL_API_KEY")
expectedKey == "" {
 = "dev-internal-key-change-in-production"
apiKey != expectedKey {
(403, gin.H{"error": "Invalid internal API key"})

ext()
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
