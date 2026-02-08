// SyncFlow – Real-Time Bidding Engine with GlobalBudgetOptimizer
// Gin-based API, < 1ms latency, automated cross-platform budget optimization
package main

import (
	"context"
	"kiki-agent-syncflow/app"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

func main() {
	// Initialize GlobalBudgetOptimizer
	syncValueAddr := getEnv("SYNCVALUE_ADDR", "http://syncvalue:8000")
	
	optimizer, err := app.NewGlobalBudgetOptimizer(app.OptimizerConfig{
		EfficiencyThreshold: 0.15,             // 15% deviation triggers reallocation
		ReallocationPercent: 0.20,             // Shift 20% of budget
		CheckInterval:       5 * time.Minute,  // Run every 5 minutes
		SyncValueAddr:       syncValueAddr,
	})
	if err != nil {
		log.Fatalf("❌ Failed to initialize GlobalBudgetOptimizer: %v", err)
	}
	
	app.SetGlobalOptimizer(optimizer)
	
	// Start background optimization
	if err := optimizer.Start(); err != nil {
		log.Fatalf("❌ Failed to start GlobalBudgetOptimizer: %v", err)
	}
	defer optimizer.Stop()
	
	// Start HTTP server
	router := app.NewRouter()
	srv := &http.Server{
		Addr:    ":8000",
		Handler: router,
	}
	
	// Graceful shutdown
	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("❌ Failed to start server: %v", err)
		}
	}()
	
	log.Println("✅ SyncFlow started on :8000 with GlobalBudgetOptimizer")
	
	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	
	log.Println("🛑 Shutting down server...")
	
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatal("❌ Server forced to shutdown:", err)
	}
	
	log.Println("✅ Server exited")
}

func getEnv(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}
