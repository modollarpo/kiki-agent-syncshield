package safefail

import (
	"encoding/json"
	"net/http"
)

// REST endpoint for manual trigger and status
func (s *SafeFailGuard) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodPost:
		// Manual trigger
		err := s.RollbackFunc("Manual Safe-Fail Triggered via API")
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte("Rollback failed: " + err.Error()))
			return
		}
		w.Write([]byte("Rollback triggered"))
	case http.MethodGet:
		// Status
		status := map[string]interface{}{
			"lastScore":     s.lastScore,
			"thresholdDrop": s.ThresholdDrop,
			"thresholdNeg":  s.ThresholdNeg,
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(status)
	default:
		w.WriteHeader(http.StatusMethodNotAllowed)
	}
}
