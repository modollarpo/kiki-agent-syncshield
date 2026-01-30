package safefail

import (
	"bytes"
	"context"
	"log"
	"net/http"
)

// Rollback logic for SyncFlow, SyncCreate, etc.
func RollbackAll(reason string) error {
	// Example: Call SyncFlow and SyncCreate REST endpoints
	ctx := context.Background()
	if err := callRollbackEndpoint(ctx, "http://syncflow:8080/rollback", reason); err != nil {
		return err
	}
	if err := callRollbackEndpoint(ctx, "http://synccreate:8080/rollback", reason); err != nil {
		return err
	}
	// Add more as needed
	return nil
}

func callRollbackEndpoint(ctx context.Context, url, reason string) error {
	payload := []byte(`{"reason": "` + reason + `"}`)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 300 {
		log.Printf("[SafeFail] Rollback endpoint %s returned %d", url, resp.StatusCode)
		return err
	}
	log.Printf("[SafeFail] Rollback called on %s", url)
	return nil
}
