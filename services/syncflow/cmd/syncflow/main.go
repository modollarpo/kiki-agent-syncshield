package main

import (
	"kiki-agent-syncflow/app"
)

// @title SyncFlow Real-Time Bidding API
// @description High-performance bidding engine (<1ms latency)
func main() {
	r := app.NewRouter()
	r.Run(":8000")
}
