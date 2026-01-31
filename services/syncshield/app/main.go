// SyncShield – Compliance Agent
// GoLang, GDPR/CCPA logging, audit trails
package main

import (
	"time"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	otelgin "go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"

	// Handler logic moved to handlers package

	handlers "kiki-agent-syncshield/services/syncshield/app/handlers"
)

func main() {
	if err := InitDB(); err != nil {
		panic("DB init failed: " + err.Error())
	}
	_ = InitS3() // S3 is optional
	r := gin.Default()
	r.Use(prometheusMiddleware)
	r.Use(otelgin.Middleware("syncshield"))
	r.POST("/audit", handlers.Audit)
	r.POST("/risk-scan", handlers.RiskScan)
	r.GET("/logs", handlers.GetLogs)
	r.GET("/logs/decrypt", handlers.GetDecryptedLogs) // admin only
	r.GET("/healthz", handlers.HealthCheck)
	r.GET("/metrics", gin.WrapH(promhttp.Handler()))
	r.Run(":8000")
}

// Prometheus metrics
var (
	requestCount = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "syncshield_requests_total",
			Help: "Total requests",
		},
		[]string{"endpoint", "method"},
	)
	errorCount = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "syncshield_errors_total",
			Help: "Total errors",
		},
		[]string{"endpoint"},
	)
	requestLatency = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "syncshield_request_latency_seconds",
			Help:    "Request latency",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"endpoint"},
	)
)

func init() {
	prometheus.MustRegister(requestCount, errorCount, requestLatency)
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
