package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"testing"
)

func TestBidEndpoint(t *testing.T) {
	go main() // Start the server in a goroutine
	// Wait for server to start (in real test, use sync or health check)
	// time.Sleep(100 * time.Millisecond)

	bid := map[string]interface{}{
		"UserID":   "testuser",
		"Features": []float32{0.1, 0.2},
	}
	body, _ := json.Marshal(bid)
	resp, err := http.Post("http://localhost:8000/bid", "application/json", bytes.NewBuffer(body))
	if err != nil {
		t.Fatalf("Failed to POST /bid: %v", err)
	}
	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected 200 OK, got %d", resp.StatusCode)
	}
}
