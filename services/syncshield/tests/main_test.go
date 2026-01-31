// Unit tests for SyncShield
package app_test

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"kiki-agent-syncshield/app/handlers"

	"github.com/gin-gonic/gin"
)

func TestHealthCheck(t *testing.T) {
	r := gin.Default()
	r.GET("/healthz", handlers.HealthCheck)
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/healthz", nil)
	r.ServeHTTP(w, req)
	if w.Code != 200 {
		t.Fatalf("expected 200, got %d", w.Code)
	}
}

func TestAuditAndLogs(t *testing.T) {
	r := gin.Default()
	r.POST("/audit", handlers.Audit)
	r.GET("/logs", handlers.GetLogs)
	r.GET("/logs/decrypt", handlers.GetDecryptedLogs)
	// Send audit events
	w := httptest.NewRecorder()
	body1 := strings.NewReader(`{"event":"plan_executed","user_id":"u1","data":{}}`)
	req, _ := http.NewRequest("POST", "/audit", body1)
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)
	w4 := httptest.NewRecorder()
	body2 := strings.NewReader(`{"event":"risk_scan","user_id":"u2","data":{}}`)
	req4, _ := http.NewRequest("POST", "/audit", body2)
	req4.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w4, req4)
	// Get logs (all)
	w2 := httptest.NewRecorder()
	req2, _ := http.NewRequest("GET", "/logs", nil)
	r.ServeHTTP(w2, req2)
	if w2.Code != 200 {
		t.Fatalf("expected 200, got %d", w2.Code)
	}
	// Get logs filtered by user_id
	w2b := httptest.NewRecorder()
	req2b, _ := http.NewRequest("GET", "/logs?user_id=u1", nil)
	r.ServeHTTP(w2b, req2b)
	if w2b.Code != 200 {
		t.Fatalf("expected 200, got %d", w2b.Code)
	}
	// Get logs filtered by event
	w2c := httptest.NewRecorder()
	req2c, _ := http.NewRequest("GET", "/logs?event=risk_scan", nil)
	r.ServeHTTP(w2c, req2c)
	if w2c.Code != 200 {
		t.Fatalf("expected 200, got %d", w2c.Code)
	}
	// Get decrypted logs (should fail without admin token)
	w3 := httptest.NewRecorder()
	req3, _ := http.NewRequest("GET", "/logs/decrypt", nil)
	r.ServeHTTP(w3, req3)
	if w3.Code != 403 {
		t.Fatalf("expected 403, got %d", w3.Code)
	}
	// Get decrypted logs (admin)
	w3a := httptest.NewRecorder()
	req3a, _ := http.NewRequest("GET", "/logs/decrypt?user_id=u1", nil)
	req3a.Header.Set("X-Admin-Token", "supersecretadmin")
	r.ServeHTTP(w3a, req3a)
	if w3a.Code != 200 {
		t.Fatalf("expected 200, got %d", w3a.Code)
	}
	// Simulate external storage check
	if len(handlers.ExternalAuditStore) < 2 {
		t.Fatalf("external storage not updated")
	}
}

func TestRiskScan(t *testing.T) {
	r := gin.Default()
	r.POST("/risk-scan", handlers.RiskScan)
	w := httptest.NewRecorder()
	body := strings.NewReader(`{"data":{"foo":1}}`)
	req, _ := http.NewRequest("POST", "/risk-scan", body)
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)
	if w.Code != 200 {
		t.Fatalf("expected 200, got %d", w.Code)
	}
}
