// SyncFlow – Real-Time Bidding Engine
// Gin-based API, <1ms latency
package app

import (
	"encoding/json"
	"log"
	"net/http"
	"time"

	"go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"
	"go.opentelemetry.io/otel"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

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
	return r
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

// Worker pool for high concurrency
const workerCount = 16

var jobQueue = make(chan BidJob, 1024)

type BidJob struct {
	Request        *http.Request
	ResponseWriter http.ResponseWriter
}

func startWorkerPool() {
	for i := 0; i < workerCount; i++ {
		go func(id int) {
			for job := range jobQueue {
				start := time.Now()
				// Zero-allocation JSON parsing (placeholder)
				var bidReq struct {
					UserID, AdSlot string
					BidAmount      float64
				}
				_ = json.NewDecoder(job.Request.Body).Decode(&bidReq)
				// <1ms bid calculation (mock)
				bid := calculateBid(bidReq)
				json.NewEncoder(job.ResponseWriter).Encode(bid)
				_ = time.Since(start)
			}
		}(i)
	}
}

type BidResult struct {
	BidID    string `json:"bid_id"`
	Accepted bool   `json:"accepted"`
	Reason   string `json:"reason"`
}

func calculateBid(_ struct {
	UserID, AdSlot string
	BidAmount      float64
}) BidResult {
	// TODO: Real logic, <1ms
	return BidResult{BidID: "bid123", Accepted: true, Reason: "ok"}
}

// --- Clean Architecture: UseCase Layer ---

// gRPC server stub removed: no BidRequest/BidResponse in valuepb, and not used in this service.

func main() {
	go startWorkerPool()
	app := NewRouter()
	log.Fatal(app.Run(":8000"))
}
