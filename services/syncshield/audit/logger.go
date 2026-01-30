package audit

import (
	"context"
	"database/sql"
	"encoding/json"
	"net/http"
	"regexp"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// Prometheus metrics
var (
	complianceViolations = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "compliance_violation_attempts",
		Help: "Number of compliance violation attempts detected.",
	})
)

func init() {
	prometheus.MustRegister(complianceViolations)
}

// PII masking middleware for Gin
func MaskPIIMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		if c.Request.Method == http.MethodPost {
			var entry AuditEvent
			if err := c.ShouldBindJSON(&entry); err == nil {
				entry = maskPII(entry)
				c.Set("maskedEntry", entry)
			}
		}
		c.Next()
	}
}

// Heartbeat endpoint for dashboard
func SecurityStatus(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}

// Gin setup for audit logging and heartbeat
func SetupRouter(auditor Auditor) *gin.Engine {
	r := gin.Default()
	r.Use(MaskPIIMiddleware())

	r.POST("/audit", func(c *gin.Context) {
		entry, exists := c.Get("maskedEntry")
		if !exists {
			c.JSON(http.StatusBadRequest, gin.H{"error": "invalid entry"})
			return
		}
		logEntry := entry.(AuditEvent)
		ctx, cancel := context.WithTimeout(c.Request.Context(), 100*time.Millisecond)
		defer cancel()
		err := auditor.LogEvent(ctx, logEntry)
		if err != nil {
			complianceViolations.Inc()
			c.JSON(http.StatusInternalServerError, gin.H{"error": "log failed"})
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": "logged"})
	})

	r.GET("/security_status", SecurityStatus)
	r.GET("/metrics", gin.WrapH(promhttp.Handler()))
	r.GET("/healthz", func(c *gin.Context) { c.String(200, "ok") })

	return r
}

type Auditor interface {
	LogEvent(ctx context.Context, event AuditEvent) error
}

type AuditEvent struct {
	UserID    string
	BidID     string
	Amount    float64
	Email     string
	IP        string
	Timestamp time.Time
}

type PgAuditor struct {
	db *sql.DB
}

func NewPgAuditor(connStr string) (*PgAuditor, error) {
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, err
	}
	return &PgAuditor{db: db}, nil
}

func (a *PgAuditor) LogEvent(ctx context.Context, event AuditEvent) error {
	masked := maskPII(event)
	data, _ := json.Marshal(masked)
	_, err := a.db.ExecContext(ctx, `INSERT INTO compliance_ledger (event) VALUES ($1)`, string(data))
	return err
}

func maskPII(e AuditEvent) AuditEvent {
	emailRe := regexp.MustCompile(`([\w.%+-]+)@([\w.-]+)\.(\w+)`)
	ipRe := regexp.MustCompile(`(\d+\.\d+\.\d+)\.\d+`)
	e.Email = emailRe.ReplaceAllString(e.Email, "***@***.***")
	e.IP = ipRe.ReplaceAllString(e.IP, "$1.***")
	return e
}
