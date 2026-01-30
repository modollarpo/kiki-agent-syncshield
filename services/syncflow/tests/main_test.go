// Unit tests for SyncFlow

package app

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"kiki-agent-syncflow/app"

	"github.com/gin-gonic/gin"
)

func setupRouter() *gin.Engine {
	r := gin.Default()
	r.POST("/execute-bid", app.ExecuteBid)
	r.POST("/allocate-budget", app.AllocateBudget)
	r.GET("/healthz", app.HealthCheck)
	return r
}

func TestHealthCheck(t *testing.T) {
	r := setupRouter()
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/healthz", nil)
	r.ServeHTTP(w, req)
	if w.Code != 200 {
		t.Fatalf("expected 200, got %d", w.Code)
	}
}

func TestExecuteBid_Valid(t *testing.T) {
	r := setupRouter()
	w := httptest.NewRecorder()
	body := `{"user_id": "u1", "context": {"priority": 2}}`
	req, _ := http.NewRequest("POST", "/execute-bid",
		strings.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)
	if w.Code != 200 {
		t.Fatalf("expected 200, got %d", w.Code)
	}
}

func TestExecuteBid_Invalid(t *testing.T) {
	r := setupRouter()
	w := httptest.NewRecorder()
	body := `{"user_id": "", "context": {}}`
	req, _ := http.NewRequest("POST", "/execute-bid",
		strings.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)
	if w.Code != 400 {
		t.Fatalf("expected 400, got %d", w.Code)
	}
}

func TestAllocateBudget_Valid(t *testing.T) {
	r := setupRouter()
	w := httptest.NewRecorder()
	body := `{"campaign_id": "c1", "amount": 100}`
	req, _ := http.NewRequest("POST", "/allocate-budget",
		strings.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)
	if w.Code != 200 {
		t.Fatalf("expected 200, got %d", w.Code)
	}
}

func TestAllocateBudget_Invalid(t *testing.T) {
	r := setupRouter()
	w := httptest.NewRecorder()
	body := `{"campaign_id": "", "amount": 0}`
	req, _ := http.NewRequest("POST", "/allocate-budget",
		strings.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)
	if w.Code != 400 {
		t.Fatalf("expected 400, got %d", w.Code)
	}
}
